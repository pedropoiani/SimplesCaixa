# 🔒 Guia de Segurança - PDV-MF

## ⚠️ ARQUIVOS QUE NUNCA DEVEM SER COMMITADOS

Os seguintes arquivos/diretórios contêm informações sensíveis e **NUNCA** devem ser enviados para o GitHub:

### 🔴 CRÍTICO - Dados Sensíveis

1. **`.env`** - Contém chaves secretas, senhas de banco de dados
2. **`instance/*.db`** - Banco de dados com dados reais dos clientes
3. **`*.pem`, `*.key`, `*.cert`** - Chaves de criptografia e certificados
4. **`vapid_private.pem`** - Chave privada para notificações push
5. **Backups do banco** - `*.backup`, `*.bak`, pasta `backups/`

### 🟡 IMPORTANTE - Cache e Temporários

6. **`__pycache__/`** - Cache do Python (desnecessário no repositório)
7. **`venv/`, `env/`** - Ambiente virtual Python (deve ser recriado)
8. **`*.log`** - Logs podem conter informações sensíveis
9. **`data/`** - Dados locais e uploads

### 🔵 RECOMENDADO - Configurações Locais

10. **`nginx.conf`** - Pode conter IPs e configurações específicas
11. **`pdv-mf.service`** - Configuração específica do servidor
12. **`.vscode/`, `.idea/`** - Configurações pessoais do IDE
13. **`docker-compose.override.yml`** - Configurações locais do Docker

---

## ✅ O QUE ESTÁ PROTEGIDO

O arquivo `.gitignore` está configurado para ignorar automaticamente:

- ✅ Todas as variações de `.env` (exceto `.env.example`)
- ✅ Bancos de dados SQLite
- ✅ Arquivos de chaves e certificados
- ✅ Cache e arquivos temporários
- ✅ Ambientes virtuais Python
- ✅ Logs e backups
- ✅ Configurações de IDEs
- ✅ Arquivos do sistema operacional

---

## 🛡️ ANTES DE FAZER COMMIT

### Checklist de Segurança:

```bash
# 1. Verifique se há arquivos sensíveis
git status

# 2. Se vir algum arquivo .env, .db, .pem, PARE!
# Adicione-os ao .gitignore se ainda não estiver

# 3. Verifique o que será commitado
git diff --cached

# 4. Se tudo estiver limpo, commit
git commit -m "Sua mensagem"
```

---

## 🚨 SE VOCÊ JÁ COMMITOU ALGO SENSÍVEL

### Remoção Imediata (antes de fazer push):

```bash
# Remover arquivo do último commit
git rm --cached .env
git commit --amend
```

### Se já fez push para o GitHub:

1. **MUDE IMEDIATAMENTE todas as senhas/chaves expostas**
2. **Remova o arquivo do histórico:**

```bash
# Instale o BFG Repo Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/

# Remova o arquivo do histórico
java -jar bfg.jar --delete-files .env

# Force push (CUIDADO!)
git push --force
```

3. **Ou crie um novo repositório limpo:**

```bash
# Remova o .git antigo
rm -rf .git

# Inicie novo repositório
git init
git add .
git commit -m "Initial commit - clean"

# Crie novo repositório no GitHub e push
```

---

## 🔑 GERANDO CHAVES SEGURAS

### Secret Key para Flask:

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Chaves VAPID para Notificações Push:

```python
python -c "from pywebpush import webpush; keys = webpush.generate_vapid_keys(); print(f'Public: {keys[\"public_key\"]}\nPrivate: {keys[\"private_key\"]}')"
```

---

## 📋 CONFIGURAÇÃO SEGURA EM PRODUÇÃO

### 1. Variáveis de Ambiente

**NUNCA** coloque senhas direto no código. Use:

```python
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### 2. Plataformas de Hospedagem

Configure variáveis de ambiente diretamente na plataforma:

**Render.com:**
- Dashboard → Environment → Add Environment Variable

**Railway:**
- Variables → Raw Editor → Cole suas variáveis

**Heroku:**
```bash
heroku config:set SECRET_KEY=sua-chave
```

**VPS (com systemd):**
```ini
[Service]
Environment="SECRET_KEY=sua-chave"
Environment="DATABASE_URL=postgresql://..."
```

### 3. Banco de Dados

- ✅ Use PostgreSQL em produção (não SQLite)
- ✅ Senhas fortes (mínimo 16 caracteres)
- ✅ Backups criptografados
- ✅ Acesso restrito por IP
- ✅ SSL/TLS ativado

---

## 🔍 AUDITORIA DE SEGURANÇA

### Verificar se há segredos no código:

```bash
# Procurar por possíveis senhas/chaves
grep -r "password\|secret\|key" --include="*.py" --exclude-dir=venv

# Verificar arquivos grandes (possível banco de dados)
find . -type f -size +1M -not -path "./venv/*" -not -path "./.git/*"
```

### Ferramentas Recomendadas:

- **GitGuardian** - Detecta segredos no código
- **git-secrets** - Previne commit de dados sensíveis
- **truffleHog** - Busca por credenciais no histórico

---

## 📚 RECURSOS ADICIONAIS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Flask Security Checklist](https://flask.palletsprojects.com/en/2.3.x/security/)

---

## ✉️ REPORTAR VULNERABILIDADES

Se você encontrar uma vulnerabilidade de segurança neste projeto:

1. **NÃO** abra uma issue pública
2. Entre em contato diretamente (se houver contato de suporte)
3. Forneça detalhes da vulnerabilidade
4. Aguarde resposta antes de divulgar publicamente

---

**Lembre-se: Segurança não é opcional! 🔒**
