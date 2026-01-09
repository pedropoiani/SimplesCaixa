#!/bin/bash

# Script de Setup Automático para Ubuntu + Cloudflare Tunnel
# Domínio: cx-mf.top

set -e  # Parar em caso de erro

echo "=========================================="
echo "🚀 Setup SimplesCaixa com Cloudflare Tunnel"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está rodando como usuário normal
if [ "$EUID" -eq 0 ]; then 
   echo -e "${RED}❌ Não execute este script como root!${NC}"
   echo "Execute como usuário normal (o script pedirá sudo quando necessário)"
   exit 1
fi

echo -e "${BLUE}📋 Passo 1/7: Atualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget software-properties-common

echo ""
echo -e "${BLUE}🐳 Passo 2/7: Instalando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✅ Docker instalado${NC}"
else
    echo -e "${GREEN}✅ Docker já está instalado${NC}"
fi

echo ""
echo -e "${BLUE}🐳 Passo 3/7: Instalando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo apt install -y docker-compose
    echo -e "${GREEN}✅ Docker Compose instalado${NC}"
else
    echo -e "${GREEN}✅ Docker Compose já está instalado${NC}"
fi

echo ""
echo -e "${BLUE}☁️  Passo 4/7: Instalando cloudflared...${NC}"
if ! command -v cloudflared &> /dev/null; then
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
    echo -e "${GREEN}✅ cloudflared instalado${NC}"
else
    echo -e "${GREEN}✅ cloudflared já está instalado${NC}"
fi

echo ""
echo -e "${BLUE}🔧 Passo 5/7: Configurando aplicação...${NC}"

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "Criando arquivo .env..."
    SECRET_KEY=$(openssl rand -hex 32)
    cat > .env << EOF
# Configurações da Aplicação
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
DATABASE_URL=postgresql://pdvuser:pdvpass@db:5432/pdvmf

# Configurações do Banco de Dados
POSTGRES_USER=pdvuser
POSTGRES_PASSWORD=pdvpass
POSTGRES_DB=pdvmf
EOF
    echo -e "${GREEN}✅ Arquivo .env criado${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

# Criar diretório para dados
mkdir -p data

echo ""
echo -e "${BLUE}🔥 Passo 6/7: Configurando firewall...${NC}"
if ! command -v ufw &> /dev/null; then
    sudo apt install -y ufw
fi

# Permitir SSH antes de habilitar
sudo ufw --force enable
sudo ufw allow OpenSSH
echo -e "${GREEN}✅ Firewall configurado (apenas SSH permitido)${NC}"

echo ""
echo -e "${BLUE}📦 Passo 7/7: Criando script de backup...${NC}"
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER=$(docker ps --filter "name=db" --format "{{.Names}}" | head -1)
if [ ! -z "$CONTAINER" ]; then
    docker exec $CONTAINER pg_dump -U pdvuser pdvmf > $BACKUP_DIR/backup_$DATE.sql
    find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
    echo "Backup criado: backup_$DATE.sql"
else
    echo "Container do banco não encontrado!"
fi
EOF
chmod +x ~/backup-db.sh
echo -e "${GREEN}✅ Script de backup criado em ~/backup-db.sh${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Instalação básica concluída!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📝 PRÓXIMOS PASSOS MANUAIS:${NC}"
echo ""
echo "1️⃣  Autenticar com Cloudflare:"
echo "   ${GREEN}cloudflared tunnel login${NC}"
echo ""
echo "2️⃣  Criar túnel:"
echo "   ${GREEN}cloudflared tunnel create simplescaixa${NC}"
echo "   (Anote o UUID do túnel!)"
echo ""
echo "3️⃣  Criar config do túnel (substitua <TUNNEL_UUID>):"
echo "   ${GREEN}sudo mkdir -p /etc/cloudflared${NC}"
echo "   ${GREEN}sudo nano /etc/cloudflared/config.yml${NC}"
echo ""
echo "   Conteúdo:"
echo "   ---"
echo "   tunnel: <TUNNEL_UUID>"
echo "   credentials-file: $HOME/.cloudflared/<TUNNEL_UUID>.json"
echo ""
echo "   ingress:"
echo "     - hostname: cx-mf.top"
echo "       service: http://127.0.0.1:5000"
echo "     - hostname: www.cx-mf.top"
echo "       service: http://127.0.0.1:5000"
echo "     - service: http_status:404"
echo "   ---"
echo ""
echo "4️⃣  Configurar DNS:"
echo "   ${GREEN}cloudflared tunnel route dns simplescaixa cx-mf.top${NC}"
echo "   ${GREEN}cloudflared tunnel route dns simplescaixa www.cx-mf.top${NC}"
echo ""
echo "5️⃣  Instalar e iniciar serviço:"
echo "   ${GREEN}sudo cloudflared service install${NC}"
echo "   ${GREEN}sudo systemctl start cloudflared${NC}"
echo "   ${GREEN}sudo systemctl enable cloudflared${NC}"
echo ""
echo "6️⃣  Iniciar aplicação:"
echo "   ${GREEN}docker-compose up -d --build${NC}"
echo ""
echo "7️⃣  Verificar:"
echo "   ${GREEN}docker-compose logs -f${NC}"
echo "   ${GREEN}sudo systemctl status cloudflared${NC}"
echo ""
echo "8️⃣  Acessar: ${GREEN}https://cx-mf.top${NC}"
echo ""
echo "=========================================="
echo -e "${RED}⚠️  IMPORTANTE:${NC} Se você adicionou seu usuário ao grupo docker,"
echo "   você precisa sair e entrar novamente (ou executar: newgrp docker)"
echo "=========================================="
