#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de tema e cores personalizadas da loja
Cores baseadas na identidade visual da MF
"""

import os

# ============================================================
# CORES DA LOJA MF
# ============================================================

# Cor principal - Preto/Cinza escuro (baseado nas logos)
COR_PRIMARIA = "#1a1a1a"
COR_PRIMARIA_ESCURA = "#0d0d0d"
COR_PRIMARIA_CLARA = "#2d2d2d"

# Cor secundária - Vermelho elegante (destaque)
COR_SECUNDARIA = "#c0392b"
COR_SECUNDARIA_ESCURA = "#962d22"
COR_SECUNDARIA_CLARA = "#e74c3c"

# Cor de destaque/sucesso
COR_SUCESSO = "#27ae60"
COR_SUCESSO_ESCURA = "#1e8449"
COR_SUCESSO_CLARA = "#2ecc71"

# Cor de alerta
COR_ALERTA = "#f39c12"
COR_ALERTA_ESCURA = "#d68910"

# Cor de perigo/erro
COR_PERIGO = "#c0392b"
COR_PERIGO_ESCURA = "#962d22"

# Cores de fundo
COR_FUNDO = "#f5f5f5"
COR_FUNDO_ESCURA = "#e8e8e8"
COR_FUNDO_CARD = "#ffffff"

# Cores de texto
COR_TEXTO = "#1a1a1a"
COR_TEXTO_SECUNDARIO = "#555555"
COR_TEXTO_CLARO = "#ffffff"

# Cores do teclado numérico
COR_TECLADO_NUMERO = "#1a1a1a"
COR_TECLADO_ESPECIAL = "#c0392b"
COR_TECLADO_CONFIRMAR = "#27ae60"
COR_TECLADO_APAGAR = "#c0392b"

# ============================================================
# CAMINHOS DOS LOGOS
# ============================================================

def obter_caminho_base():
    """Retorna o caminho base da aplicação"""
    return os.path.dirname(os.path.abspath(__file__))

def obter_logo_completa():
    """Logo completa horizontal - ideal para cabeçalhos largos"""
    return os.path.join(obter_caminho_base(), "logos", "logo_completa.png")

def obter_logo_perfil():
    """Logo de perfil quadrada - ideal para ícones e PDF"""
    return os.path.join(obter_caminho_base(), "logos", "logo_de_perfil.jpg")

def obter_logo_informativa():
    """Logo informativa - ideal para relatórios"""
    return os.path.join(obter_caminho_base(), "logos", "logo_informativa.jpg")

# ============================================================
# ESTILOS DE BOTÕES
# ============================================================

ESTILO_BTN_PRIMARIO = {
    "bg": COR_PRIMARIA,
    "fg": COR_TEXTO_CLARO,
    "activebackground": COR_PRIMARIA_ESCURA,
    "activeforeground": COR_TEXTO_CLARO,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

ESTILO_BTN_SECUNDARIO = {
    "bg": COR_SECUNDARIA,
    "fg": COR_TEXTO_CLARO,
    "activebackground": COR_SECUNDARIA_ESCURA,
    "activeforeground": COR_TEXTO_CLARO,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

ESTILO_BTN_SUCESSO = {
    "bg": COR_SUCESSO,
    "fg": COR_TEXTO_CLARO,
    "activebackground": COR_SUCESSO_ESCURA,
    "activeforeground": COR_TEXTO_CLARO,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

ESTILO_BTN_PERIGO = {
    "bg": COR_PERIGO,
    "fg": COR_TEXTO_CLARO,
    "activebackground": COR_PERIGO_ESCURA,
    "activeforeground": COR_TEXTO_CLARO,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

ESTILO_BTN_NEUTRO = {
    "bg": "#95a5a6",
    "fg": COR_TEXTO_CLARO,
    "activebackground": "#7f8c8d",
    "activeforeground": COR_TEXTO_CLARO,
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0
}

# ============================================================
# NOME DA LOJA
# ============================================================

NOME_LOJA = "MF"
NOME_SISTEMA = f"PDV {NOME_LOJA}"
SUBTITULO_SISTEMA = "Sistema de Controle de Caixa"
