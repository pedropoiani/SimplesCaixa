#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para sincronização de movimentações com GitHub Pages
Usa a API do GitHub diretamente (não precisa do Git instalado)
"""

import os
import json
import base64
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class GitHubSync:
    """Classe para sincronizar dados com GitHub Pages via API"""
    
    def __init__(self, config_path: str = None):
        """
        Inicializa o sincronizador
        
        Args:
            config_path: Caminho para o arquivo de configuração
        """
        if config_path is None:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".pdvmf")
            os.makedirs(app_dir, exist_ok=True)
            config_path = os.path.join(app_dir, "github_config.json")
        
        self.config_path = config_path
        self.config = self._carregar_config()
    
    def _carregar_config(self) -> Dict:
        """Carrega configurações do arquivo"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'token': '',
            'repo': '',  # formato: usuario/repositorio
            'ativo': False
        }
    
    def salvar_config(self, token: str, repo: str, ativo: bool = True):
        """
        Salva as configurações do GitHub
        
        Args:
            token: Token de acesso pessoal do GitHub
            repo: Repositório no formato 'usuario/repositorio'
            ativo: Se a sincronização está ativa
        """
        self.config = {
            'token': token,
            'repo': repo,
            'ativo': ativo
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def esta_configurado(self) -> bool:
        """Verifica se a sincronização está configurada e ativa"""
        return (
            self.config.get('ativo', False) and
            bool(self.config.get('token')) and
            bool(self.config.get('repo'))
        )
    
    def _obter_sha_arquivo(self, caminho: str) -> Optional[str]:
        """
        Obtém o SHA atual do arquivo no GitHub (necessário para atualização)
        
        Args:
            caminho: Caminho do arquivo no repositório
            
        Returns:
            SHA do arquivo ou None se não existir
        """
        url = f"https://api.github.com/repos/{self.config['repo']}/contents/{caminho}"
        
        headers = {
            'Authorization': f"token {self.config['token']}",
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PDV-MF-Sync'
        }
        
        try:
            req = urllib.request.Request(url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('sha')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # Arquivo não existe
            raise
        except Exception:
            return None
    
    def _enviar_arquivo(self, caminho: str, conteudo: str, mensagem: str) -> bool:
        """
        Envia ou atualiza um arquivo no GitHub via API
        
        Args:
            caminho: Caminho do arquivo no repositório
            conteudo: Conteúdo do arquivo
            mensagem: Mensagem do commit
            
        Returns:
            True se sucesso, False se falha
        """
        url = f"https://api.github.com/repos/{self.config['repo']}/contents/{caminho}"
        
        headers = {
            'Authorization': f"token {self.config['token']}",
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'PDV-MF-Sync'
        }
        
        # Codificar conteúdo em Base64
        conteudo_base64 = base64.b64encode(conteudo.encode('utf-8')).decode('utf-8')
        
        # Obter SHA se arquivo já existe
        sha = self._obter_sha_arquivo(caminho)
        
        payload = {
            'message': mensagem,
            'content': conteudo_base64,
            'branch': 'main'
        }
        
        if sha:
            payload['sha'] = sha
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status in [200, 201]
        except urllib.error.HTTPError as e:
            print(f"Erro HTTP ao sincronizar: {e.code} - {e.reason}")
            return False
        except Exception as e:
            print(f"Erro ao sincronizar com GitHub: {e}")
            return False
    
    def sincronizar_movimentacoes(self, movimentacoes: List[Dict]) -> bool:
        """
        Sincroniza as movimentações com o GitHub Pages
        
        Args:
            movimentacoes: Lista de movimentações dos últimos 4 dias
            
        Returns:
            True se sucesso, False se falha
        """
        if not self.esta_configurado():
            return False
        
        # Preparar dados
        dados = {
            'atualizadoEm': datetime.now().isoformat(),
            'movimentacoes': movimentacoes
        }
        
        conteudo = json.dumps(dados, indent=2, ensure_ascii=False, default=str)
        mensagem = f"Atualiza movimentações - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        return self._enviar_arquivo('docs/movimentacoes.json', conteudo, mensagem)
    
    def testar_conexao(self) -> tuple:
        """
        Testa a conexão com o GitHub
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        if not self.config.get('token') or not self.config.get('repo'):
            return False, "Token ou repositório não configurados"
        
        url = f"https://api.github.com/repos/{self.config['repo']}"
        
        headers = {
            'Authorization': f"token {self.config['token']}",
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'PDV-MF-Sync'
        }
        
        try:
            req = urllib.request.Request(url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return True, f"Conectado ao repositório: {data.get('full_name')}"
        except urllib.error.HTTPError as e:
            if e.code == 401:
                return False, "Token inválido ou expirado"
            elif e.code == 404:
                return False, "Repositório não encontrado"
            else:
                return False, f"Erro HTTP: {e.code}"
        except Exception as e:
            return False, f"Erro de conexão: {str(e)}"


def obter_movimentacoes_ultimos_dias(db, dias: int = 4) -> List[Dict]:
    """
    Obtém movimentações dos últimos N dias do banco de dados
    
    Args:
        db: Instância do Database
        dias: Número de dias para buscar
        
    Returns:
        Lista de movimentações
    """
    data_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    data_fim = datetime.now().strftime('%Y-%m-%d')
    
    movimentacoes = db.listar_lancamentos(
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    # Converter para formato serializável
    resultado = []
    for mov in movimentacoes:
        resultado.append({
            'id': mov.get('id'),
            'tipo': mov.get('tipo'),
            'categoria': mov.get('categoria'),
            'valor': mov.get('valor'),
            'forma_pagamento_nome': mov.get('forma_pagamento_nome'),
            'observacao': mov.get('observacao'),
            'data_hora': mov.get('data_hora'),
            'operador': mov.get('operador')
        })
    
    return resultado


# Instância global (será inicializada quando necessário)
_github_sync = None


def get_github_sync() -> GitHubSync:
    """Obtém a instância do sincronizador (singleton)"""
    global _github_sync
    if _github_sync is None:
        _github_sync = GitHubSync()
    return _github_sync


def sincronizar_agora(db) -> bool:
    """
    Função de conveniência para sincronizar imediatamente
    
    Args:
        db: Instância do Database
        
    Returns:
        True se sucesso, False se falha ou não configurado
    """
    sync = get_github_sync()
    if not sync.esta_configurado():
        return False
    
    movimentacoes = obter_movimentacoes_ultimos_dias(db, dias=4)
    return sync.sincronizar_movimentacoes(movimentacoes)
