#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para salvar movimentações do caixa em JSON
Para sincronização em tempo real via GitHub + Vercel
"""

import json
import os
from datetime import datetime

# Caminho do arquivo JSON
CAMINHO_JSON = os.path.join(os.path.dirname(__file__), 'public', 'data', 'movimentacoes.json')

# Controle de sincronização automática
SYNC_AUTOMATICO = True  # Mude para False se não quiser sincronizar automaticamente


def _sincronizar_github():
    """Sincroniza com GitHub se habilitado"""
    if not SYNC_AUTOMATICO:
        return
    try:
        from github_sync import sincronizar_json
        sincronizar_json()
    except ImportError:
        pass  # Módulo não disponível
    except Exception as e:
        print(f"⚠️ Erro ao sincronizar com GitHub: {e}")


def garantir_pasta():
    """Cria pasta se não existir"""
    pasta = os.path.dirname(CAMINHO_JSON)
    if not os.path.exists(pasta):
        os.makedirs(pasta)


def carregar_movimentacoes():
    """Carrega movimentações do JSON"""
    garantir_pasta()
    if os.path.exists(CAMINHO_JSON):
        with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"caixa_aberto": None, "movimentacoes": [], "ultima_atualizacao": None}


def salvar_movimentacoes(dados):
    """Salva movimentações no JSON"""
    garantir_pasta()
    with open(CAMINHO_JSON, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registrar_movimentacao(tipo: str, valor: float, descricao: str = "", forma_pagamento: str = ""):
    """
    Registra uma nova movimentação no caixa
    
    Args:
        tipo: 'entrada' ou 'saida'
        valor: valor da movimentação
        descricao: descrição da movimentação
        forma_pagamento: dinheiro, pix, cartao, etc
    """
    dados = carregar_movimentacoes()
    
    nova = {
        "id": len(dados["movimentacoes"]) + 1,
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "forma_pagamento": forma_pagamento,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    dados["movimentacoes"].append(nova)
    dados["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    salvar_movimentacoes(dados)
    _sincronizar_github()  # Sync automático
    return nova


def abrir_caixa_json(valor_inicial: float, operador: str = ""):
    """Registra abertura do caixa no JSON"""
    dados = {
        "caixa_aberto": {
            "valor_inicial": valor_inicial,
            "operador": operador,
            "data_abertura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "movimentacoes": [],
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    salvar_movimentacoes(dados)
    _sincronizar_github()  # Sync automático


def fechar_caixa_json():
    """Registra fechamento do caixa no JSON"""
    dados = carregar_movimentacoes()
    dados["caixa_aberto"] = None
    dados["data_fechamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dados["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    salvar_movimentacoes(dados)
    _sincronizar_github()  # Sync automático
    dados["ultima_atualizacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    salvar_movimentacoes(dados)


def obter_resumo():
    """Retorna resumo das movimentações"""
    dados = carregar_movimentacoes()
    
    entradas = sum(m["valor"] for m in dados["movimentacoes"] if m["tipo"] == "entrada")
    saidas = sum(m["valor"] for m in dados["movimentacoes"] if m["tipo"] == "saida")
    
    return {
        "total_entradas": entradas,
        "total_saidas": saidas,
        "saldo": entradas - saidas,
        "qtd_movimentacoes": len(dados["movimentacoes"])
    }
