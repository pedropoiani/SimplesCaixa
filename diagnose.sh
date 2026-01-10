#!/bin/bash

# Script de diagnóstico para Bad Gateway
echo "🔍 Diagnóstico - SimplesCaixa Bad Gateway"
echo "========================================"
echo ""

# 1. Status dos containers
echo "1️⃣  STATUS DOS CONTAINERS:"
docker-compose ps
echo ""

# 2. Logs do container web
echo "2️⃣  ÚLTIMOS LOGS DO WEB (últimas 30 linhas):"
docker-compose logs --tail=30 web
echo ""

# 3. Logs do database
echo "3️⃣  ÚLTIMOS LOGS DO DATABASE (últimas 20 linhas):"
docker-compose logs --tail=20 db
echo ""

# 4. Testar conexão do web ao db
echo "4️⃣  TESTANDO CONECTIVIDADE WEB -> DB:"
docker-compose exec web bash -c "curl -v http://db:5432 2>&1" || echo "DB não respondendo na porta 5432"
echo ""

# 5. Verificar se Flask está respondendo
echo "5️⃣  TESTANDO FLASK (porta 5000):"
docker-compose exec web curl -v http://localhost:5000 2>&1 | head -20
echo ""

# 6. Verificar ambiente
echo "6️⃣  VARIÁVEIS DE AMBIENTE DO WEB:"
docker-compose exec web env | grep -E "DATABASE_URL|FLASK_ENV|SECRET_KEY"
echo ""

# 7. Health check
echo "7️⃣  REINICIANDO CONTAINERS..."
docker-compose restart
sleep 5
echo "✓ Containers reiniciados"
echo ""

# 8. Status final
echo "8️⃣  STATUS FINAL:"
docker-compose ps
