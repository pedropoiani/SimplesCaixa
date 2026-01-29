# 📦 Backup Automático - Google Drive

## 🎯 Visão Geral

Sistema de backup automático que:
- 📤 Faz dump do banco PostgreSQL
- 🗜️ Comprime o backup (gzip)
- ☁️ Envia para Google Drive via rclone
- 🧹 Remove backups locais antigos (7+ dias)
- 🔄 Executa automaticamente antes de cada deploy

## 🚀 Instalação e Configuração

### 1. Instalar rclone no Servidor

```bash
# SSH no servidor
ssh pedropoiani@192.168.1.45

# Instalar rclone
sudo apt update
sudo apt install rclone -y

# Verificar instalação
rclone version
```

### 2. Configurar Google Drive

```bash
# Iniciar configuração interativa
rclone config

# Responda as perguntas:
# n) New remote
# name> gdrive
# Storage> drive  (ou número correspondente ao Google Drive)
# client_id> [deixe vazio - pressione Enter]
# client_secret> [deixe vazio - pressione Enter]
# scope> 1  (Full access)
# root_folder_id> [deixe vazio]
# service_account_file> [deixe vazio]
# Edit advanced config? n
# Use web browser to authenticate? y
```

#### ⚠️ Autenticação no Servidor Sem Interface Gráfica

Se o servidor não tem navegador, use esta opção:

```bash
# Durante o rclone config, escolha:
# Use web browser to authenticate? n

# Será gerado um link. Copie e cole no seu navegador local
# Autorize o acesso ao Google Drive
# Cole o código de autorização de volta no terminal
```

**OU** configure localmente e copie a configuração:

```bash
# No seu computador local
rclone config  # Configure o gdrive

# Copie a configuração para o servidor
scp ~/.config/rclone/rclone.conf pedropoiani@192.168.1.45:~/.config/rclone/
```

### 3. Testar Conexão

```bash
# Listar conteúdo do seu Google Drive
rclone ls gdrive:

# Criar pasta para backups
rclone mkdir gdrive:SimplesCaixa/Backups

# Verificar pasta criada
rclone lsf gdrive:SimplesCaixa/
```

### 4. Testar Backup Manual

```bash
cd /home/pedropoiani/simplescaixa
./backup-gdrive.sh
```

Você deve ver:
```
🔄 BACKUP AUTOMÁTICO - Google Drive
====================================

✓ Diretório de backup: ./backups

➤ PASSO 1: Backup do Banco de Dados
  • Fazendo dump via Docker...
✓ Backup criado: pdvmf_backup_20260128_143022.sql (2.3M)

➤ PASSO 2: Comprimindo Backup
✓ Backup comprimido: pdvmf_backup_20260128_143022.sql.gz (456K)

➤ PASSO 3: Upload para Google Drive
  • Enviando para: gdrive:SimplesCaixa/Backups/
✓ Upload concluído com sucesso!
✓ Arquivo verificado no Google Drive

✅ BACKUP CONCLUÍDO!
```

## 📋 Uso

### Backup Manual

```bash
cd /home/pedropoiani/simplescaixa
./backup-gdrive.sh
```

### Backup Automático no Deploy

O backup é executado **automaticamente** antes de cada deploy:

```bash
# Local
./deploy-remoto.sh

# O deploy fará:
# 1. Pull do código
# 2. ✨ BACKUP AUTOMÁTICO ✨
# 3. Parar containers
# 4. Rebuild
# 5. Iniciar containers
```

### Agendar Backups Diários (Cron)

```bash
# Editar crontab no servidor
crontab -e

# Adicionar linha (backup todo dia às 3h da manhã)
0 3 * * * cd /home/pedropoiani/simplescaixa && ./backup-gdrive.sh >> /tmp/backup.log 2>&1
```

## 🔄 Restauração

### 1. Listar Backups Disponíveis

```bash
# Via rclone
rclone ls gdrive:SimplesCaixa/Backups/

# Ou pelo Google Drive web
# https://drive.google.com
```

### 2. Baixar Backup

```bash
# Baixar backup específico
rclone copy "gdrive:SimplesCaixa/Backups/pdvmf_backup_20260128_143022.sql.gz" ./

# Descompactar
gunzip pdvmf_backup_20260128_143022.sql.gz
```

### 3. Restaurar no PostgreSQL

```bash
# Parar aplicação
docker-compose stop web

# Restaurar banco
docker-compose exec -T db psql -U postgres -d pdvmf < pdvmf_backup_20260128_143022.sql

# Reiniciar
docker-compose start web
```

### 4. Restaurar do SQLite

```bash
# Se o backup for SQLite (.db.gz)
gunzip pdvmf_20260128_143022.db.gz
cp pdvmf_20260128_143022.db instance/pdvmf.db
```

## 📊 Gerenciamento

### Ver Backups Locais

```bash
ls -lh backups/
```

### Ver Backups no Google Drive

```bash
rclone ls gdrive:SimplesCaixa/Backups/
```

### Deletar Backups Antigos do Google Drive

```bash
# Deletar backups com mais de 30 dias
rclone delete gdrive:SimplesCaixa/Backups/ --min-age 30d

# Ou deletar arquivo específico
rclone delete gdrive:SimplesCaixa/Backups/arquivo_antigo.sql.gz
```

### Espaço Utilizado

```bash
rclone size gdrive:SimplesCaixa/Backups/
```

## ⚙️ Configurações

### Alterar Retenção Local

Edite `backup-gdrive.sh`:

```bash
RETENTION_DAYS=7  # Manter backups dos últimos 7 dias localmente
```

### Alterar Pasta no Google Drive

Edite `backup-gdrive.sh`:

```bash
GDRIVE_FOLDER="SimplesCaixa/Backups"  # Mudar para outra pasta
```

### Notificações (Opcional)

Adicione ao final de `backup-gdrive.sh`:

```bash
# Enviar email de confirmação
echo "Backup concluído: ${COMPRESSED_FILE}" | mail -s "Backup SimplesCaixa" seu@email.com

# Ou webhook do Slack/Discord
curl -X POST https://hooks.slack.com/... -d "{\"text\":\"Backup concluído!\"}"
```

## 🔒 Segurança

### ✅ Boas Práticas

- ✅ Backups são **criptografados em trânsito** (HTTPS/TLS)
- ✅ Autenticação OAuth2 com Google
- ✅ Tokens armazenados em `~/.config/rclone/rclone.conf`
- ✅ Backups comprimidos economizam espaço
- ✅ Retenção local limitada (7 dias)

### ⚠️ Importantes

- 🔐 Proteja o arquivo `~/.config/rclone/rclone.conf` (contém tokens)
- 🔐 Use autenticação 2FA na sua conta Google
- 📝 Teste restauração periodicamente
- 🧪 Valide integridade dos backups

## 🐛 Solução de Problemas

### Erro: "rclone not found"

```bash
sudo apt install rclone -y
```

### Erro: "Google Drive não configurado"

```bash
rclone config
# Configure conforme instruções acima
```

### Erro: "Failed to copy"

```bash
# Verificar conectividade
rclone about gdrive:

# Reautenticar se necessário
rclone config reconnect gdrive:
```

### Erro: "Container do banco não está rodando"

Certifique-se que os containers estão ativos:

```bash
docker-compose ps
docker-compose up -d
```

### Backup muito lento

```bash
# Use rclone com múltiplas threads
rclone copy --transfers=4 --checkers=8 ...
```

## 📈 Monitoramento

### Verificar Último Backup

```bash
# Local
ls -lht backups/ | head -3

# Google Drive
rclone ls gdrive:SimplesCaixa/Backups/ | tail -5
```

### Logs de Backup

```bash
# Ver log do cron
tail -f /tmp/backup.log

# Ver logs do rclone
rclone ls gdrive: -vv
```

## 🎁 Recursos Extras

### Backup Incremental

```bash
# Sincronizar apenas mudanças
rclone sync backups/ gdrive:SimplesCaixa/Backups/
```

### Backup Criptografado

Configure rclone crypt para criptografar backups:

```bash
rclone config
# n) New remote
# name> gdrive-crypt
# type> crypt
# remote> gdrive:SimplesCaixa/Backups
# password> [sua senha forte]
```

### Múltiplos Destinos

Edite script para fazer backup em múltiplos locais:

```bash
# Google Drive
rclone copy ... gdrive:...

# Dropbox
rclone copy ... dropbox:...

# AWS S3
rclone copy ... s3:bucket/...
```

## 📞 Suporte

Problemas? Verifique:
- 📖 [Documentação do rclone](https://rclone.org/docs/)
- 💬 [Fórum rclone](https://forum.rclone.org/)
- 🐛 [Issues do rclone](https://github.com/rclone/rclone/issues)

---

**✨ Seus dados estão seguros!** 🔒
