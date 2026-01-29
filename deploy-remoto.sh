#!/bin/bash

# Deploy remoto via SSH - Passo a passo
# Preserva banco de dados existente

set -e

SERVIDOR="pedropoiani@192.168.1.45"
CAMINHO_REMOTO="/home/pedropoiani/SimplesCaixa"

echo "🚀 DEPLOY REMOTO - SimplesCaixa"
echo "================================"
echo ""
echo "📍 Servidor: $SERVIDOR"
echo "📂 Caminho: $CAMINHO_REMOTO"
echo ""

# Passo 1: Conectar e validar
echo "➤ PASSO 1: Validando conexão SSH..."
ssh "$SERVIDOR" "echo '✓ Conectado com sucesso'" || exit 1
echo ""

# Passo 2: Puxar código
echo "➤ PASSO 2: Puxando código do GitHub..."
ssh "$SERVIDOR" << 'SCRIPT'
cd /home/pedropoiani/SimplesCaixa || cd ~/SimplesCaixa || exit 1
pwd
echo "Branches disponíveis:"
git branch -a
echo ""
echo "Puxando main..."
git pull origin main
echo "✓ Código atualizado"
SCRIPT
echo ""

# Passo 3: Parar containers
echo "➤ PASSO 3: Parando containers..."
ssh "$SERVIDOR" << 'SCRIPT'
cd /home/pedropoiani/SimplesCaixa || cd ~/SimplesCaixa
echo "Containers atuais:"
docker-compose ps
echo ""
echo "Parando..."
docker-compose down --remove-orphans
echo "✓ Containers parados"
SCRIPT
echo ""

# Passo 4: Iniciar novos containers
echo "➤ PASSO 4: Iniciando novos containers (preservando DB)..."
ssh "$SERVIDOR" << 'SCRIPT'
cd /home/pedropoiani/SimplesCaixa || cd ~/SimplesCaixa
docker-compose up -d --build
echo "✓ Containers iniciados"
SCRIPT
echo ""

# Passo 5: Aguardar inicialização
echo "➤ PASSO 5: Aguardando inicialização (30s)..."
sleep 30
echo "✓ Pronto"
echo ""

# Passo 6: Verificar saúde
echo "➤ PASSO 6: Verificando status..."
ssh "$SERVIDOR" << 'SCRIPT'
cd /home/pedropoiani/SimplesCaixa || cd ~/SimplesCaixa
echo "Status dos containers:"
docker-compose ps
echo ""
echo "Health check:"
curl -s http://localhost:5000/health 2>/dev/null | python3 -m json.tool || echo "⚠️  Endpoint indisponível (aplicação pode estar inicializando)"
SCRIPT
echo ""

# Resumo final
echo "✅ DEPLOY CONCLUÍDO!"
echo ""
echo "📊 Informações úteis:"
echo "  • URL: http://192.168.1.45:5000"
echo "  • Health: http://192.168.1.45:5000/health"
echo ""
echo "🔍 Para ver logs em tempo real:"
echo "  ssh $SERVIDOR 'cd SimplesCaixa && docker-compose logs -f web'"
echo ""
echo "⚠️  Dados do banco de dados foram preservados"
echo ""
