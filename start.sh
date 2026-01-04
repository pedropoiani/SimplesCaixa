#!/bin/bash

echo "🚀 PDV-MF Web - Iniciando..."
echo ""

# Verificar se está no diretório correto
if [ ! -f "run.py" ]; then
    echo "❌ Erro: Execute este script na pasta do projeto"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python 3 não encontrado"
    echo "Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar/criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -q -r requirements.txt

# Verificar/criar arquivo .env
if [ ! -f ".env" ]; then
    echo "⚙️  Criando arquivo .env..."
    cp .env.example .env
    echo "✏️  IMPORTANTE: Edite o arquivo .env e configure o SECRET_KEY!"
fi

# Limpar terminal
clear

echo "✅ PDV-MF Web iniciado!"
echo ""
echo "🌐 Acesse: http://localhost:5000"
echo ""
echo "Para parar: Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Executar aplicação
python3 run.py
