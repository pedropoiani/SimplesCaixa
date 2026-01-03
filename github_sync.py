#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para sincronização automática com GitHub
Usa a API do GitHub para fazer commits do arquivo JSON
"""

import requests
import base64
import json
import os
from datetime import datetime

# ============================================
# CONFIGURAÇÃO - PREENCHA COM SEUS DADOS
# ============================================
GITHUB_TOKEN = "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"  # Seu Personal Access Token
GITHUB_OWNER = "pedropoiani"  # Seu usuário do GitHub (ex: "pedropoiani")
GITHUB_REPO = "SimplesCaixa"   # Nome do repositório (ex: "pdvMF")
GITHUB_BRANCH = "caixa-loja"  # Branch do repositório
# ============================================

# Caminho do arquivo no repositório
ARQUIVO_JSON = "public/data/movimentacoes.json"

# Arquivo de configuração local
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '.github_config.json')


def carregar_config():
    """Carrega configuração do arquivo local"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def salvar_config(config):
    """Salva configuração no arquivo local"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def configurar_github(token: str, owner: str, repo: str, branch: str = "main"):
    """
    Configura as credenciais do GitHub
    
    Args:
        token: Personal Access Token do GitHub
        owner: Usuário/organização do GitHub
        repo: Nome do repositório
        branch: Branch para commits (default: main)
    """
    config = {
        "token": token,
        "owner": owner,
        "repo": repo,
        "branch": branch
    }
    salvar_config(config)
    print("✅ Configuração do GitHub salva com sucesso!")
    return True


def obter_credenciais():
    """Obtém credenciais do GitHub (arquivo ou variáveis globais)"""
    # Primeiro tenta do arquivo de config
    config = carregar_config()
    if config.get("token"):
        return config
    
    # Depois tenta das variáveis globais
    if GITHUB_TOKEN:
        return {
            "token": GITHUB_TOKEN,
            "owner": GITHUB_OWNER,
            "repo": GITHUB_REPO,
            "branch": GITHUB_BRANCH
        }
    
    return None


def obter_arquivo_github():
    """Obtém o conteúdo atual do arquivo no GitHub"""
    creds = obter_credenciais()
    if not creds:
        print("❌ GitHub não configurado. Use configurar_github() primeiro.")
        return None, None
    
    url = f"https://api.github.com/repos/{creds['owner']}/{creds['repo']}/contents/{ARQUIVO_JSON}"
    
    headers = {
        "Authorization": f"token {creds['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    params = {"ref": creds['branch']}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            conteudo = base64.b64decode(data['content']).decode('utf-8')
            sha = data['sha']
            return conteudo, sha
        elif response.status_code == 404:
            # Arquivo não existe ainda
            return None, None
        else:
            print(f"❌ Erro ao obter arquivo: {response.status_code}")
            print(response.json())
            return None, None
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None, None


def enviar_para_github(conteudo: str, mensagem: str = None):
    """
    Envia o arquivo JSON para o GitHub
    
    Args:
        conteudo: Conteúdo do arquivo JSON (string)
        mensagem: Mensagem do commit (opcional)
    """
    creds = obter_credenciais()
    if not creds:
        print("❌ GitHub não configurado. Use configurar_github() primeiro.")
        return False
    
    url = f"https://api.github.com/repos/{creds['owner']}/{creds['repo']}/contents/{ARQUIVO_JSON}"
    
    headers = {
        "Authorization": f"token {creds['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Obter SHA atual do arquivo (necessário para atualizar)
    _, sha = obter_arquivo_github()
    
    # Mensagem do commit
    if not mensagem:
        mensagem = f"Atualiza movimentações - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    
    # Preparar dados
    data = {
        "message": mensagem,
        "content": base64.b64encode(conteudo.encode('utf-8')).decode('utf-8'),
        "branch": creds['branch']
    }
    
    # Se arquivo já existe, incluir SHA
    if sha:
        data["sha"] = sha
    
    try:
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            print(f"✅ Sincronizado com GitHub: {mensagem}")
            return True
        else:
            print(f"❌ Erro ao enviar para GitHub: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


def sincronizar_json():
    """Sincroniza o arquivo JSON local com o GitHub"""
    from salvar_json import CAMINHO_JSON
    
    if not os.path.exists(CAMINHO_JSON):
        print("❌ Arquivo JSON local não encontrado")
        return False
    
    with open(CAMINHO_JSON, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    return enviar_para_github(conteudo)


def testar_conexao():
    """Testa a conexão com o GitHub"""
    creds = obter_credenciais()
    if not creds:
        print("❌ GitHub não configurado")
        return False
    
    url = f"https://api.github.com/repos/{creds['owner']}/{creds['repo']}"
    
    headers = {
        "Authorization": f"token {creds['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo = response.json()
            print(f"✅ Conectado ao repositório: {repo['full_name']}")
            print(f"   Branch padrão: {repo['default_branch']}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


# ============================================
# EXEMPLO DE USO
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    print("Configuração do GitHub para PDV-MF")
    print("=" * 50)
    print()
    print("Para configurar, execute no Python:")
    print()
    print('from github_sync import configurar_github')
    print('configurar_github(')
    print('    token="ghp_seu_token_aqui",')
    print('    owner="seu_usuario",')
    print('    repo="pdvMF",')
    print('    branch="caixa-loja"')
    print(')')
    print()
    print("Para testar a conexão:")
    print('from github_sync import testar_conexao')
    print('testar_conexao()')
