#!/bin/bash

# ==========================================
# SETUP BACKUP - Guia Interativo
# ==========================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  📦 SETUP BACKUP - GOOGLE DRIVE PASSO A PASSO  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""

# PASSO 1
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASSO 1/5: Verificando rclone${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if command -v rclone &> /dev/null; then
    echo -e "${GREEN}✓ rclone já instalado!${NC}"
    rclone version | head -1
else
    echo -e "${YELLOW}⚠️  rclone não encontrado. Instalando...${NC}"
    echo ""
    echo "Execute o comando:"
    echo -e "${BLUE}sudo apt update && sudo apt install rclone -y${NC}"
    echo ""
    read -p "Pressione ENTER depois de instalar..."
fi

echo ""

# PASSO 2
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASSO 2/5: Verificando Google Drive${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if rclone listremotes 2>/dev/null | grep -q "^gdrive:$"; then
    echo -e "${GREEN}✓ Google Drive já configurado!${NC}"
    echo ""
    echo "Testando conexão..."
    rclone about gdrive: 2>/dev/null && echo -e "${GREEN}✓ Conexão OK!${NC}" || echo -e "${YELLOW}⚠️  Reconecte: rclone config reconnect gdrive:${NC}"
else
    echo -e "${YELLOW}⚠️  Google Drive NÃO configurado${NC}"
    echo ""
    echo "Vou abrir o assistente de configuração."
    echo ""
    echo -e "${BLUE}INSTRUÇÕES:${NC}"
    echo "  1. Digite: ${GREEN}n${NC} (New remote)"
    echo "  2. Nome: ${GREEN}gdrive${NC}"
    echo "  3. Storage: ${GREEN}drive${NC} (Google Drive)"
    echo "  4. client_id: ${GREEN}[deixe vazio - pressione ENTER]${NC}"
    echo "  5. client_secret: ${GREEN}[deixe vazio - pressione ENTER]${NC}"
    echo "  6. scope: ${GREEN}1${NC} (Full access)"
    echo "  7. root_folder_id: ${GREEN}[deixe vazio]${NC}"
    echo "  8. service_account_file: ${GREEN}[deixe vazio]${NC}"
    echo "  9. Edit advanced config? ${GREEN}n${NC}"
    echo "  10. Use web browser? ${GREEN}y${NC} (ou ${GREEN}n${NC} se não tiver interface gráfica)"
    echo ""
    read -p "Pressione ENTER para iniciar configuração..."
    
    rclone config
    
    echo ""
    echo "Configuração concluída!"
fi

echo ""

# PASSO 3
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASSO 3/5: Criando pasta no Google Drive${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Criando: SimplesCaixa/Backups/"
rclone mkdir gdrive:SimplesCaixa/Backups/ 2>/dev/null || true

echo "Verificando..."
if rclone lsf gdrive:SimplesCaixa/ 2>/dev/null | grep -q "Backups"; then
    echo -e "${GREEN}✓ Pasta criada com sucesso!${NC}"
else
    echo -e "${YELLOW}⚠️  Não foi possível verificar a pasta${NC}"
fi

echo ""

# PASSO 4
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASSO 4/5: Testando backup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd ~/simplescaixa || cd /home/pedropoiani/simplescaixa || { echo "Diretório não encontrado"; exit 1; }

if [ -f "backup-gdrive.sh" ]; then
    echo "Executando backup de teste..."
    echo ""
    bash backup-gdrive.sh
    echo ""
    echo -e "${GREEN}✓ Backup executado!${NC}"
else
    echo -e "${YELLOW}⚠️  Script backup-gdrive.sh não encontrado${NC}"
    echo "Faça git pull primeiro"
fi

echo ""

# PASSO 5
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}PASSO 5/5: Configurar backups diários (OPCIONAL)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Deseja agendar backup automático diário às 3h da manhã?"
read -p "Digite 's' para sim ou 'n' para pular: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    CRON_CMD="0 3 * * * cd $(pwd) && ./backup-gdrive.sh >> /tmp/backup-simplescaixa.log 2>&1"
    
    # Verificar se já existe
    if crontab -l 2>/dev/null | grep -q "backup-gdrive.sh"; then
        echo -e "${YELLOW}⚠️  Backup já está agendado no cron${NC}"
    else
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓ Backup diário configurado!${NC}"
        echo ""
        echo "Para ver os logs:"
        echo "  tail -f /tmp/backup-simplescaixa.log"
    fi
else
    echo "Pulando agendamento."
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ CONFIGURAÇÃO CONCLUÍDA!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📊 Comandos úteis:"
echo "  • Backup manual:        ./backup-gdrive.sh"
echo "  • Ver backups:          rclone ls gdrive:SimplesCaixa/Backups/"
echo "  • Espaço usado:         rclone size gdrive:SimplesCaixa/Backups/"
echo "  • Testar conexão:       rclone about gdrive:"
echo ""
echo "🚀 O próximo deploy fará backup automático!"
echo ""
