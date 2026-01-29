# 🔒 Segurança - SimplesCaixa

## 📋 Visão Geral

Este documento descreve as práticas de segurança implementadas no projeto SimplesCaixa e orientações para manter a aplicação segura.

## 🛡️ Proteções Implementadas

### 1. Controle de Versão (.gitignore)

O `.gitignore` está configurado para **NUNCA** permitir que arquivos sensíveis sejam commitados:

#### 🔴 CRÍTICO - Nunca Commitar
- **Bancos de dados**: `*.db`, `*.sqlite`, `*.sql`, `data/`
- **Variáveis de ambiente**: `.env`, `.env.*` (exceto `.env.example`)
- **Chaves e certificados**: `*.pem`, `*.key`, `*.crt`, `*.p12`, `id_rsa*`
- **Credenciais**: `secrets.yml`, `credentials.json`, `*.password`
- **Senhas e tokens**: `password.txt`, `api_key*`, `*.token`

#### 🟡 SENSÍVEL - Dados Pessoais
- **Logs**: `*.log`, `logs/` (podem conter informações sensíveis)
- **Backups**: `*.backup`, `*.bak`, `backup/`
- **Dados financeiros**: `*.csv`, `*.xlsx`, relatórios PDFs
- **Uploads**: `uploads/`, `media/`, `user_files/`

#### 🔵 Desenvolvimento
- **Ambientes Python**: `venv/`, `__pycache__/`, `*.pyc`
- **IDEs**: `.vscode/`, `.idea/`, `*.swp`
- **Testes**: `test_*.pdf`, `test_*.db`, `.pytest_cache/`
- **Cache**: `.cache/`, `tmp/`, `*.tmp`

### 2. Verificação Automática (check_security.sh)

Antes de cada commit, o script `check_security.sh` verifica:
- ✅ Arquivos `.env` estão ignorados
- ✅ Bancos de dados não estão sendo commitados
- ✅ Chaves e certificados estão protegidos
- ✅ Cache Python está ignorado
- ✅ Ambiente virtual está ignorado
- ✅ Nenhum segredo detectado no código

### 3. Banco de Dados

#### Produção (Docker)
- PostgreSQL em container isolado
- Volume persistente para dados
- Credenciais via variáveis de ambiente
- Sem acesso direto externo (apenas via aplicação)

#### Desenvolvimento (SQLite)
- Arquivo local `instance/pdvmf.db`
- **NUNCA commitado** no Git
- Backup local recomendado

### 4. Variáveis de Ambiente

```bash
# ❌ NUNCA faça isso
git add .env
git commit -m "adiciona configurações"

# ✅ Faça isso
cp .env.example .env
# Edite .env com suas credenciais locais
# .env será ignorado automaticamente
```

#### Variáveis Sensíveis
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=sua-chave-secreta-aqui
FLASK_SECRET_KEY=outra-chave-secreta
```

### 5. Deploy Seguro

O script `deploy-remoto.sh` implementa:
- 🔐 Conexão SSH com autenticação
- 📦 Build isolado em container Docker
- 🗄️ Preservação de dados do banco
- 🔄 Restart automático com health check
- 📝 Logs de auditoria

## 🚨 Procedimentos de Segurança

### Antes de Commitar

1. **Verifique o status**: `git status`
2. **Revise as mudanças**: `git diff`
3. **Confie no check_security.sh**: ele executa automaticamente
4. **Em caso de dúvida**: não commite, pergunte primeiro

### Se Você Commitou Algo Sensível

#### 🔴 AÇÃO IMEDIATA NECESSÁRIA

```bash
# 1. Remova do último commit (se ainda não deu push)
git reset HEAD~1
git add .gitignore
git commit -m "fix: remove arquivo sensível"

# 2. Se já deu push, reescreva o histórico
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch arquivo-sensivel.txt" \
  --prune-empty --tag-name-filter cat -- --all

# 3. Force push (CUIDADO!)
git push origin --force --all

# 4. MUDE IMEDIATAMENTE as credenciais expostas
```

⚠️ **IMPORTANTE**: Se credenciais foram expostas publicamente, considere-as **COMPROMETIDAS** e mude-as **IMEDIATAMENTE**.

### Rotação de Credenciais

Recomendação de rotação:
- 🔴 **Produção**: A cada 90 dias ou se suspeitar de comprometimento
- 🟡 **Desenvolvimento**: A cada 6 meses
- 🟢 **Testes**: Sempre que necessário

### Backup do Banco de Dados

```bash
# Produção (via Docker)
ssh usuario@servidor 'cd simplescaixa && docker-compose exec db pg_dump -U postgres pdvmf > backup_$(date +%Y%m%d).sql'

# Desenvolvimento (SQLite)
cp instance/pdvmf.db backups/pdvmf_$(date +%Y%m%d).db
```

## 📖 Boas Práticas

### ✅ FAÇA

- Use variáveis de ambiente para credenciais
- Mantenha `.env.example` atualizado (sem valores reais)
- Revise mudanças antes de commitar
- Use senhas fortes e únicas
- Mantenha dependências atualizadas
- Faça backups regulares do banco
- Use HTTPS em produção
- Monitore logs regularmente

### ❌ NÃO FAÇA

- Commitar arquivos `.env`
- Commitar bancos de dados
- Commitar chaves privadas
- Hardcodear senhas no código
- Desabilitar o `check_security.sh`
- Compartilhar credenciais de produção
- Usar mesma senha em dev e prod
- Ignorar avisos de segurança

## 🔍 Auditoria

### Verificar Histórico do Git

```bash
# Procurar por possíveis credenciais
git log -S "password" --all
git log -S "secret" --all
git log -S "api_key" --all

# Ver o que foi commitado
git log --stat
git log --oneline --graph
```

### Verificar Arquivos Ignorados

```bash
# Listar arquivos ignorados
git status --ignored

# Verificar se um arquivo específico está ignorado
git check-ignore -v arquivo.txt
```

## 🆘 Contato de Segurança

Se você descobrir uma vulnerabilidade de segurança:

1. **NÃO** crie uma issue pública
2. **NÃO** publique a vulnerabilidade
3. Entre em contato diretamente com o mantenedor
4. Aguarde confirmação antes de divulgar

## 📚 Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/latest/security/)
- [Git Security Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage)
- [Docker Security](https://docs.docker.com/engine/security/)

## 📝 Changelog de Segurança

### v1.1.0 (2026-01-28)
- ✅ Melhorado `.gitignore` com proteções abrangentes
- ✅ Removidos PDFs de teste do repositório
- ✅ Documentação de segurança criada
- ✅ Verificação automática funcionando

---

**Lembre-se**: Segurança é responsabilidade de todos! 🔒
