#!/bin/bash

# ==========================================
# BACKUP AUTOMÁTICO PARA GOOGLE DRIVE
# ==========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 BACKUP AUTOMÁTICO - Google Drive${NC}"
echo "===================================="
echo ""

# Configurações
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_BACKUP_FILE="pdvmf_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=7  # Manter backups dos últimos 7 dias localmente

# Configuração do Google Drive (via rclone)
GDRIVE_REMOTE="gdrive"  # Nome configurado no rclone
GDRIVE_FOLDER="SimplesCaixa/Backups"

# ==========================================
# FUNÇÕES
# ==========================================

check_rclone() {
    if ! command -v rclone &> /dev/null; then
        echo -e "${RED}❌ rclone não encontrado!${NC}"
        echo ""
        echo "Instale o rclone:"
        echo "  Ubuntu/Debian: sudo apt install rclone"
        echo "  ou visite: https://rclone.org/install/"
        echo ""
        echo "Depois configure o Google Drive:"
        echo "  rclone config"
        exit 1
    fi
}

check_gdrive_config() {
    if ! rclone listremotes | grep -q "^${GDRIVE_REMOTE}:$"; then
        echo -e "${YELLOW}⚠️  Google Drive não configurado!${NC}"
        echo ""
        echo "Configure o rclone com o Google Drive:"
        echo "  rclone config"
        echo ""
        echo "Escolha:"
        echo "  • n) New remote"
        echo "  • Nome: ${GDRIVE_REMOTE}"
        echo "  • Storage: Google Drive (drive)"
        echo "  • Siga as instruções para autenticar"
        echo ""
        exit 1
    fi
}

create_backup_dir() {
    mkdir -p "${BACKUP_DIR}"
    echo -e "${GREEN}✓${NC} Diretório de backup: ${BACKUP_DIR}"
}

backup_database() {
    echo ""
    echo -e "${BLUE}➤ PASSO 1: Backup do Banco de Dados${NC}"
    
    # Verificar se está rodando via Docker
    if docker-compose ps db 2>/dev/null | grep -q "Up"; then
        echo "  • Fazendo dump via Docker..."
        docker-compose exec -T db pg_dump -U pdvuser pdvmf > "${BACKUP_DIR}/${DB_BACKUP_FILE}"
        
        if [ -f "${BACKUP_DIR}/${DB_BACKUP_FILE}" ]; then
            SIZE=$(du -h "${BACKUP_DIR}/${DB_BACKUP_FILE}" | cut -f1)
            echo -e "${GREEN}✓${NC} Backup criado: ${DB_BACKUP_FILE} (${SIZE})"
        else
            echo -e "${RED}❌ Falha ao criar backup${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠️  Container do banco não está rodando${NC}"
        echo "  • Tentando backup do SQLite local..."
        
        if [ -f "instance/pdvmf.db" ]; then
            cp instance/pdvmf.db "${BACKUP_DIR}/pdvmf_${TIMESTAMP}.db"
            SIZE=$(du -h "${BACKUP_DIR}/pdvmf_${TIMESTAMP}.db" | cut -f1)
            echo -e "${GREEN}✓${NC} Backup SQLite criado: pdvmf_${TIMESTAMP}.db (${SIZE})"
        else
            echo -e "${RED}❌ Nenhum banco de dados encontrado${NC}"
            exit 1
        fi
    fi
}

compress_backup() {
    echo ""
    echo -e "${BLUE}➤ PASSO 2: Comprimindo Backup${NC}"
    
    cd "${BACKUP_DIR}"
    
    if [ -f "${DB_BACKUP_FILE}" ]; then
        gzip -f "${DB_BACKUP_FILE}"
        COMPRESSED_FILE="${DB_BACKUP_FILE}.gz"
        SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
        echo -e "${GREEN}✓${NC} Backup comprimido: ${COMPRESSED_FILE} (${SIZE})"
    elif [ -f "pdvmf_${TIMESTAMP}.db" ]; then
        gzip -f "pdvmf_${TIMESTAMP}.db"
        COMPRESSED_FILE="pdvmf_${TIMESTAMP}.db.gz"
        SIZE=$(du -h "${COMPRESSED_FILE}" | cut -f1)
        echo -e "${GREEN}✓${NC} Backup comprimido: ${COMPRESSED_FILE} (${SIZE})"
    else
        echo -e "${RED}❌ Arquivo de backup não encontrado${NC}"
        exit 1
    fi
    
    cd ..
}

upload_to_gdrive() {
    echo ""
    echo -e "${BLUE}➤ PASSO 3: Upload para Google Drive${NC}"
    
    echo "  • Enviando para: ${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/"
    
    if rclone copy "${BACKUP_DIR}/${COMPRESSED_FILE}" "${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/" --progress; then
        echo -e "${GREEN}✓${NC} Upload concluído com sucesso!"
        
        # Verificar no Google Drive
        echo ""
        echo "  • Verificando arquivo no Google Drive..."
        if rclone ls "${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/${COMPRESSED_FILE}" &> /dev/null; then
            REMOTE_SIZE=$(rclone ls "${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/${COMPRESSED_FILE}" | awk '{print $1}')
            echo -e "${GREEN}✓${NC} Arquivo verificado no Google Drive (${REMOTE_SIZE} bytes)"
        fi
    else
        echo -e "${RED}❌ Falha no upload${NC}"
        exit 1
    fi
}

cleanup_old_backups() {
    echo ""
    echo -e "${BLUE}➤ PASSO 4: Limpeza de Backups Antigos${NC}"
    
    # Limpar backups locais antigos
    echo "  • Removendo backups locais com mais de ${RETENTION_DAYS} dias..."
    find "${BACKUP_DIR}" -name "*.gz" -type f -mtime +${RETENTION_DAYS} -delete
    
    LOCAL_COUNT=$(ls -1 "${BACKUP_DIR}"/*.gz 2>/dev/null | wc -l)
    echo -e "${GREEN}✓${NC} Backups locais mantidos: ${LOCAL_COUNT}"
    
    # Listar backups no Google Drive
    echo ""
    echo "  • Backups no Google Drive:"
    rclone ls "${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/" | tail -5
}

show_summary() {
    echo ""
    echo "===================================="
    echo -e "${GREEN}✅ BACKUP CONCLUÍDO!${NC}"
    echo "===================================="
    echo ""
    echo "📊 Informações:"
    echo "  • Arquivo: ${COMPRESSED_FILE}"
    echo "  • Local: ${BACKUP_DIR}/"
    echo "  • Google Drive: ${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/"
    echo ""
    echo "🔍 Para restaurar:"
    echo "  rclone copy \"${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/${COMPRESSED_FILE}\" ./"
    echo "  gunzip ${COMPRESSED_FILE}"
    echo ""
    echo "📁 Ver backups no Google Drive:"
    echo "  rclone ls \"${GDRIVE_REMOTE}:${GDRIVE_FOLDER}/\""
    echo ""
}

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

# Verificações
check_rclone
check_gdrive_config

# Executar backup
create_backup_dir
backup_database
compress_backup
upload_to_gdrive
cleanup_old_backups
show_summary
