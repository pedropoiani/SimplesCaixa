# 🚀 Guia Rápido: Git + GitHub com Segurança

## 📋 Checklist Antes do Primeiro Push

- [x] ✅ `.gitignore` configurado
- [x] ✅ `.env.example` criado (sem dados reais)
- [x] ✅ `.env` protegido (não será commitado)
- [x] ✅ Bancos de dados protegidos
- [x] ✅ Script de verificação criado

## 🎯 Comandos para Enviar ao GitHub

### 1️⃣ Criar Repositório no GitHub

1. Acesse https://github.com
2. Clique em "+" → "New repository"
3. Nome: `SimplesCaixa`
4. **NÃO** marque "Initialize with README" (já temos um)
5. Clique em "Create repository"

### 2️⃣ Conectar e Enviar

```bash
# Verificar segurança PRIMEIRO!
./check_security.sh

# Se tudo OK, adicione os arquivos
git add .

# Faça o commit inicial
git commit -m "🎉 Initial commit - Sistema PDV-MF"

# Conecte ao repositório remoto (substitua SEU_USUARIO)
git remote add origin https://github.com/pedropoiani/SimplesCaixa.git

# Renomeie a branch para main (opcional mas recomendado)
git branch -M main

# Envie para o GitHub
git push -u origin main
```

### 3️⃣ Futuras Atualizações

```bash
# Sempre verifique a segurança antes
./check_security.sh

# Adicione as mudanças
git add .

# Commit com mensagem descritiva
git commit -m "✨ Descrição da mudança"

# Envie para o GitHub
git push
```

## 🔒 Verificações de Segurança Automáticas

### Opção 1: Hook do Git (Recomendado)

Crie um hook que verifica automaticamente antes de cada commit:

```bash
# Criar o hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
./check_security.sh
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Commit bloqueado por questões de segurança!"
    echo "Resolva os problemas acima antes de commitar."
    exit 1
fi
EOF

# Tornar executável
chmod +x .git/hooks/pre-commit
```

Agora toda vez que você fizer `git commit`, o script de segurança rodará automaticamente!

### Opção 2: Verificação Manual

Sempre execute antes de commitar:

```bash
./check_security.sh && git add . && git commit -m "Sua mensagem"
```

## ⚠️ O QUE NUNCA FAZER

### ❌ NUNCA commite:

```bash
# ❌ NÃO faça isso!
git add .env
git add instance/*.db
git add *.key
git add *.pem

# ✅ Faça isso:
git add .env.example
```

### ❌ NUNCA adicione senhas no código:

```python
# ❌ ERRADO
DATABASE_URL = "postgresql://user:senha123@host/db"

# ✅ CORRETO
DATABASE_URL = os.getenv('DATABASE_URL')
```

## 🆘 Se Você Commitou Algo Sensível

### Antes de fazer `push`:

```bash
# Remover arquivo do commit
git reset HEAD .env

# Ou desfazer o commit completamente
git reset --soft HEAD~1
```

### Depois de fazer `push`:

1. **MUDE TODAS AS SENHAS/CHAVES IMEDIATAMENTE!**
2. Remova do histórico:

```bash
# Opção 1: git-filter-repo (recomendado)
pip install git-filter-repo
git filter-repo --invert-paths --path .env
git push --force

# Opção 2: BFG Repo Cleaner
# Download: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env
git push --force
```

## 📊 Comandos Úteis do Git

```bash
# Ver status
git status

# Ver arquivos ignorados
git status --ignored

# Ver o que será commitado
git diff --cached

# Remover arquivo do staging
git reset HEAD arquivo.txt

# Ver histórico
git log --oneline

# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Ver arquivos rastreados
git ls-files

# Verificar se arquivo está ignorado
git check-ignore -v .env
```

## 🎨 Boas Práticas de Commit

### Mensagens de Commit:

Use emojis e seja descritivo:

```bash
git commit -m "✨ feat: Adiciona sistema de notificações push"
git commit -m "🐛 fix: Corrige cálculo de troco"
git commit -m "📝 docs: Atualiza README com instruções"
git commit -m "🔒 security: Melhora proteção de arquivos sensíveis"
git commit -m "♻️ refactor: Reorganiza estrutura de pastas"
git commit -m "🎨 style: Melhora interface do caixa"
git commit -m "⚡ perf: Otimiza consultas ao banco"
git commit -m "🧪 test: Adiciona testes para API"
```

### Convenções:

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração de código
- `test`: Testes
- `chore`: Tarefas de build/config
- `security`: Segurança

## 🌿 Trabalhando com Branches

```bash
# Criar nova branch para feature
git checkout -b feature/nova-funcionalidade

# Voltar para main
git checkout main

# Merge da feature
git merge feature/nova-funcionalidade

# Deletar branch
git branch -d feature/nova-funcionalidade
```

## 📦 Arquivo .gitignore Completo

Seu `.gitignore` já está configurado para proteger:

```gitignore
# Dados sensíveis
.env
.env.*
!.env.example

# Bancos de dados
*.db
*.sqlite
*.sqlite3
instance/

# Chaves
*.pem
*.key
*.cert

# Cache e temporários
__pycache__/
*.pyc
venv/
*.log

# IDEs
.vscode/
.idea/
```

## ✅ Resumo

1. **Sempre** execute `./check_security.sh` antes de commitar
2. **Nunca** commite arquivos `.env`, `.db`, ou `.pem`
3. **Use** `.env.example` como template
4. **Configure** hooks do Git para verificação automática
5. **Mude senhas** imediatamente se expor algo sensível

---

**Seu repositório está protegido! 🛡️**

Agora você pode usar o GitHub com segurança:

```bash
./check_security.sh && git add . && git commit -m "🎉 Projeto pronto"
git push
```
