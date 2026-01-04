# 🖥️ Guia de Deploy em VPS

Este guia mostra como hospedar o PDV-MF em um VPS (servidor próprio).

## Requisitos

- VPS com Ubuntu 20.04+ ou Debian 11+
- Acesso SSH root
- Domínio apontando para o IP do servidor (opcional)

---

## Opção 1: Deploy com Docker (RECOMENDADO)

### Passo 1: Conectar ao Servidor

```bash
ssh root@SEU_IP_DO_SERVIDOR
```

### Passo 2: Instalar Docker

```bash
# Atualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com | sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar instalação
docker --version
docker-compose --version
```

### Passo 3: Baixar o Projeto

```bash
# Instalar Git
apt install git -y

# Clonar repositório
cd /opt
git clone https://github.com/SEU-USUARIO/pdv-mf.git
cd pdv-mf
```

### Passo 4: Configurar Variáveis

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

Configure:
```bash
SECRET_KEY=cole-aqui-uma-chave-aleatoria-gerada
FLASK_ENV=production
DATABASE_URL=postgresql://pdvuser:pdvpass@db:5432/pdvmf
```

Gerar SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Passo 5: Iniciar Aplicação

```bash
# Subir containers
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar status
docker-compose ps
```

### Passo 6: Configurar Firewall

```bash
# Permitir SSH e HTTP/HTTPS
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### Passo 7: Configurar Nginx (Proxy Reverso)

```bash
# Instalar Nginx
apt install nginx -y

# Copiar configuração de exemplo
cp nginx.conf.example /etc/nginx/sites-available/pdv-mf

# Editar e ajustar domínio
nano /etc/nginx/sites-available/pdv-mf

# Ativar site
ln -s /etc/nginx/sites-available/pdv-mf /etc/nginx/sites-enabled/

# Remover site padrão
rm /etc/nginx/sites-enabled/default

# Testar configuração
nginx -t

# Recarregar Nginx
systemctl reload nginx
```

### Passo 8: Configurar SSL (HTTPS) - Grátis

```bash
# Instalar Certbot
apt install certbot python3-certbot-nginx -y

# Obter certificado (substitua seu-dominio.com)
certbot --nginx -d seu-dominio.com -d www.seu-dominio.com

# Renovação automática já está configurada
certbot renew --dry-run
```

**Pronto!** Acesse: `https://seu-dominio.com`

---

## Opção 2: Deploy Tradicional (Sem Docker)

### Passo 1: Preparar Servidor

```bash
# Conectar
ssh root@SEU_IP_DO_SERVIDOR

# Atualizar
apt update && apt upgrade -y

# Instalar dependências
apt install python3 python3-pip python3-venv postgresql nginx git -y
```

### Passo 2: Configurar PostgreSQL

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco e usuário
CREATE DATABASE pdvmf;
CREATE USER pdvuser WITH PASSWORD 'senha_segura_aqui';
GRANT ALL PRIVILEGES ON DATABASE pdvmf TO pdvuser;
\q
```

### Passo 3: Instalar Aplicação

```bash
# Criar diretório
mkdir -p /opt/pdv-mf
cd /opt/pdv-mf

# Clonar repositório
git clone https://github.com/SEU-USUARIO/pdv-mf.git .

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis

```bash
# Criar arquivo .env
nano .env
```

Conteúdo:
```bash
SECRET_KEY=sua-chave-aleatoria-aqui
FLASK_ENV=production
DATABASE_URL=postgresql://pdvuser:senha_segura_aqui@localhost:5432/pdvmf
PORT=5000
```

### Passo 5: Criar Serviço Systemd

```bash
# Copiar arquivo de serviço
cp pdv-mf.service.example /etc/systemd/system/pdv-mf.service

# Editar se necessário
nano /etc/systemd/system/pdv-mf.service

# Ajustar permissões
chown -R www-data:www-data /opt/pdv-mf

# Ativar e iniciar serviço
systemctl daemon-reload
systemctl enable pdv-mf
systemctl start pdv-mf

# Verificar status
systemctl status pdv-mf

# Ver logs
journalctl -u pdv-mf -f
```

### Passo 6: Configurar Nginx

```bash
# Copiar configuração
cp nginx.conf.example /etc/nginx/sites-available/pdv-mf

# Editar
nano /etc/nginx/sites-available/pdv-mf

# Ativar
ln -s /etc/nginx/sites-available/pdv-mf /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Testar e recarregar
nginx -t
systemctl reload nginx
```

### Passo 7: SSL com Certbot

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

## Comandos Úteis

### Docker

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Atualizar código
cd /opt/pdv-mf
git pull
docker-compose down
docker-compose up -d --build

# Backup do banco
docker exec pdv-mf-db pg_dump -U pdvuser pdvmf > backup.sql
```

### Systemd (Sem Docker)

```bash
# Ver status
systemctl status pdv-mf

# Ver logs
journalctl -u pdv-mf -f

# Reiniciar
systemctl restart pdv-mf

# Parar
systemctl stop pdv-mf

# Iniciar
systemctl start pdv-mf

# Atualizar código
cd /opt/pdv-mf
git pull
systemctl restart pdv-mf
```

### PostgreSQL

```bash
# Backup
pg_dump -U pdvuser pdvmf > backup_$(date +%Y%m%d).sql

# Restaurar
psql -U pdvuser pdvmf < backup.sql

# Acessar banco
sudo -u postgres psql pdvmf
```

### Nginx

```bash
# Testar configuração
nginx -t

# Recarregar
systemctl reload nginx

# Ver logs
tail -f /var/log/nginx/pdv-mf-access.log
tail -f /var/log/nginx/pdv-mf-error.log
```

---

## Segurança Adicional

### Firewall Avançado

```bash
# Bloquear tudo exceto SSH, HTTP, HTTPS
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### Fail2Ban (Proteger SSH)

```bash
# Instalar
apt install fail2ban -y

# Configurar
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
nano /etc/fail2ban/jail.local

# Iniciar
systemctl enable fail2ban
systemctl start fail2ban
```

### Atualizações Automáticas

```bash
# Instalar
apt install unattended-upgrades -y

# Configurar
dpkg-reconfigure -plow unattended-upgrades
```

---

## Monitoramento

### Instalar Htop

```bash
apt install htop -y
htop
```

### Ver Uso de Recursos

```bash
# CPU e Memória
free -h
top

# Disco
df -h

# Docker
docker stats
```

---

## Backup Automático

### Script de Backup

```bash
# Criar script
nano /opt/backup-pdv.sh
```

Conteúdo:
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup do banco (Docker)
docker exec pdv-mf-db pg_dump -U pdvuser pdvmf | gzip > $BACKUP_DIR/pdvmf_$DATE.sql.gz

# Ou sem Docker
# pg_dump -U pdvuser pdvmf | gzip > $BACKUP_DIR/pdvmf_$DATE.sql.gz

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup concluído: $DATE"
```

```bash
# Tornar executável
chmod +x /opt/backup-pdv.sh

# Agendar no cron (diariamente às 3h)
crontab -e

# Adicione:
0 3 * * * /opt/backup-pdv.sh >> /var/log/backup-pdv.log 2>&1
```

---

## Problemas Comuns

### Aplicação não inicia

```bash
# Ver logs
docker-compose logs
# ou
journalctl -u pdv-mf -f
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker-compose ps
# ou
systemctl status postgresql

# Testar conexão
psql -U pdvuser -h localhost pdvmf
```

### Nginx retorna 502

```bash
# Verificar se aplicação está rodando
docker-compose ps
# ou
systemctl status pdv-mf

# Verificar se porta está correta
netstat -tulpn | grep 5000
```

---

## Custo Estimado de VPS

| Provedor | Preço/Mês | Recursos |
|----------|-----------|----------|
| **Oracle Cloud** | Grátis | 4 vCPU, 24GB RAM (ARM) |
| **Contabo** | R$ 20 | 4 vCPU, 8GB RAM, 200GB |
| **Hetzner** | R$ 25 | 2 vCPU, 4GB RAM, 40GB |
| **DigitalOcean** | $6 (~R$ 30) | 1 vCPU, 1GB RAM, 25GB |
| **Vultr** | $6 (~R$ 30) | 1 vCPU, 1GB RAM, 25GB |

---

## Próximos Passos

1. Configure backup automático
2. Configure monitoramento (opcional: Uptime Robot)
3. Configure domínio personalizado
4. Teste a aplicação completamente
5. Configure alertas de erro (opcional)

**Seu sistema está no ar! 🚀**
