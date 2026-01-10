#!/bin/bash

# Script para fazer deploy seguro
set -e

echo "🚀 DEPLOY - SimplesCaixa"
echo "======================="
echo ""

# Validações
echo "✓ Validando repositório..."
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Erro: docker-compose.yml não encontrado!"
    exit 1
fi

# Git
echo "✓ Atualizando do GitHub..."
git pull origin main || echo "⚠️  Aviso: Pull falhou, continuando..."

# Docker
echo "✓ Reconstruindo imagem..."
docker-compose down
docker-compose up -d --build

# Aguardar inicialização
echo "⏳ Aguardando serviços ficarem prontos (30s)..."
sleep 30

# Health check
echo "🏥 Verificando saúde da aplicação..."
HEALTH=$(curl -s http://localhost:5000/health || echo "")
if echo "$HEALTH" | grep -q "ok"; then
    echo "✅ DEPLOY SUCESSO!"
    echo ""
    echo "Status dos containers:"
    docker-compose ps
else
    echo "⚠️  AVISO: Saúde não ideal, verificando logs..."
    docker-compose logs --tail=50 web
fi

echo ""
echo "📍 URL: http://localhost:5000"
echo "📊 Health: http://localhost:5000/health"
echo ""
echo "Para ver logs em tempo real:"
echo "  docker-compose logs -f web"
