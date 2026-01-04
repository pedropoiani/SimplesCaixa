#!/bin/bash

# 🔒 Script de Verificação de Segurança
# Execute antes de fazer commit para garantir que não há arquivos sensíveis

echo "🔍 Verificando arquivos sensíveis..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de problemas
PROBLEMAS=0

# 1. Verificar se .env existe e não está no .gitignore
if [ -f ".env" ]; then
    if git check-ignore .env > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Arquivo .env está protegido pelo .gitignore"
    else
        echo -e "${RED}✗${NC} PERIGO: .env existe mas NÃO está no .gitignore!"
        PROBLEMAS=$((PROBLEMAS+1))
    fi
fi

# 2. Verificar bancos de dados
echo ""
echo "📊 Verificando bancos de dados..."
DB_FILES=$(find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" | grep -v ".git" | grep -v "venv")
if [ -n "$DB_FILES" ]; then
    echo -e "${YELLOW}⚠${NC} Arquivos de banco encontrados:"
    echo "$DB_FILES"
    # Verificar se estão ignorados
    for file in $DB_FILES; do
        if ! git check-ignore "$file" > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} $file NÃO está no .gitignore!"
            PROBLEMAS=$((PROBLEMAS+1))
        fi
    done
else
    echo -e "${GREEN}✓${NC} Nenhum arquivo de banco encontrado"
fi

# 3. Verificar chaves e certificados
echo ""
echo "🔑 Verificando chaves e certificados..."
KEY_FILES=$(find . -name "*.pem" -o -name "*.key" -o -name "*.cert" -o -name "*.crt" | grep -v ".git" | grep -v "venv")
if [ -n "$KEY_FILES" ]; then
    echo -e "${YELLOW}⚠${NC} Arquivos de chave encontrados:"
    echo "$KEY_FILES"
    for file in $KEY_FILES; do
        if ! git check-ignore "$file" > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} $file NÃO está no .gitignore!"
            PROBLEMAS=$((PROBLEMAS+1))
        fi
    done
else
    echo -e "${GREEN}✓${NC} Nenhum arquivo de chave encontrado"
fi

# 4. Verificar __pycache__
echo ""
echo "🗂️  Verificando cache Python..."
if [ -d "__pycache__" ]; then
    if git check-ignore __pycache__ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} __pycache__ está protegido"
    else
        echo -e "${YELLOW}⚠${NC} __pycache__ não está no .gitignore"
    fi
fi

# 5. Verificar venv
echo ""
echo "🐍 Verificando ambiente virtual..."
if [ -d "venv" ] || [ -d "env" ]; then
    if git check-ignore venv > /dev/null 2>&1 || git check-ignore env > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ambiente virtual está protegido"
    else
        echo -e "${YELLOW}⚠${NC} Ambiente virtual não está no .gitignore"
    fi
fi

# 6. Verificar logs
echo ""
echo "📝 Verificando logs..."
LOG_FILES=$(find . -name "*.log" | grep -v ".git" | grep -v "venv")
if [ -n "$LOG_FILES" ]; then
    echo -e "${YELLOW}⚠${NC} Arquivos de log encontrados:"
    echo "$LOG_FILES"
    for file in $LOG_FILES; do
        if ! git check-ignore "$file" > /dev/null 2>&1; then
            echo -e "${RED}✗${NC} $file NÃO está no .gitignore!"
            PROBLEMAS=$((PROBLEMAS+1))
        fi
    done
else
    echo -e "${GREEN}✓${NC} Nenhum arquivo de log encontrado"
fi

# 7. Buscar por palavras suspeitas no código
echo ""
echo "🔎 Buscando por possíveis segredos no código..."
SUSPEITAS=$(grep -r -i "password.*=.*['\"].*['\"]" --include="*.py" --exclude-dir={venv,env,.git} . 2>/dev/null | grep -v ".pyc" | grep -v "exemplo" | grep -v "example")
if [ -n "$SUSPEITAS" ]; then
    echo -e "${YELLOW}⚠${NC} Possíveis senhas hardcoded encontradas:"
    echo "$SUSPEITAS"
    echo -e "${YELLOW}⚠${NC} Verifique se são apenas exemplos!"
fi

# 8. Verificar arquivos staged
echo ""
echo "📤 Verificando arquivos que serão commitados..."
STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -n "$STAGED" ]; then
    echo "Arquivos staged:"
    echo "$STAGED"
    echo ""
    # Verificar se há algo suspeito
    STAGED_SUSPEITO=$(echo "$STAGED" | grep -E '\.(env|db|sqlite|log|pem|key)$')
    if [ -n "$STAGED_SUSPEITO" ]; then
        echo -e "${RED}✗✗✗ PERIGO! Arquivos sensíveis estão staged:${NC}"
        echo "$STAGED_SUSPEITO"
        PROBLEMAS=$((PROBLEMAS+10))
    fi
else
    echo -e "${YELLOW}ℹ${NC} Nenhum arquivo staged para commit"
fi

# Resultado final
echo ""
echo "================================"
if [ $PROBLEMAS -eq 0 ]; then
    echo -e "${GREEN}✓ Tudo OK! Seguro para commit.${NC}"
    exit 0
else
    echo -e "${RED}✗ $PROBLEMAS problema(s) encontrado(s)!${NC}"
    echo -e "${RED}NÃO faça commit até resolver os problemas acima!${NC}"
    exit 1
fi
