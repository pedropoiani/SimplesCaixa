# 📋 Resumo - Fix Bad Gateway

## ✅ Mudanças Realizadas

### 1. **Health Check Endpoint** ✨
- Adicionado `/health` em `app/__init__.py`
- Retorna `{"status": "ok", "db": "connected"}` se tudo funciona
- Retorna erro 503 se banco não está conectado
- Docker usa isso para saber quando iniciar o web

### 2. **Melhor Tratamento de Banco de Dados** 🔗
- SQLAlchemy agora verifica conexão antes de usar (`pool_pre_ping`)
- Conexões recicladas a cada hora (`pool_recycle`)
- Timeout de 10s para PostgreSQL
- Erros de conexão não travam a app

### 3. **Docker Compose Melhorado** 🐳
- Adicionado `healthcheck` para PostgreSQL
- Adicionado `healthcheck` para Flask/Web
- Mudado `depends_on` para esperar DB estar `healthy` (condition: service_healthy)
- Web só inicia quando DB está pronto

### 4. **Dockerfile Melhorado** 📦
- Adicionado `curl` (necessário para health check)
- Health check integrado no Dockerfile
- Melhor logging do Gunicorn
- Timeout aumentado para 120s

### 5. **Scripts de Diagnóstico** 🔧
- `deploy.sh` - Deploy seguro com validações
- `diagnose.sh` - Diagnóstico automático de problemas
- `TROUBLESHOOTING.md` - Documentação completa de troubleshooting

### 6. **Documentação Atualizada** 📚
- DEPLOY.md atualizado com novos commands
- TROUBLESHOOTING.md criado com soluções

---

## 🚀 Como Usar

### Deploy no Servidor

```bash
ssh pedropoiani@192.168.1.45
cd simplescaixa
git pull origin main
bash deploy.sh
```

### Verificar Saúde

```bash
# Local
curl http://localhost:5000/health

# Remoto
curl http://192.168.1.45:5000/health
```

### Ver Logs em Tempo Real

```bash
docker-compose logs -f web
```

---

## 🐛 Problema Resolvido

**Antes:** Bad Gateway era um "mistério" - poderia ser:
- Flask não respondendo
- DB não conectado
- Timeout
- Qualquer coisa

**Agora:** 
- Health check mostra exatamente o que está wrong
- Docker espera DB estar pronto
- Pool de conexões mais robusto
- Logs claros de erros

---

## 📊 Checklist de Verificação

- [x] App inicia sem erros
- [x] Health check funciona localmente
- [x] Docker compose com health checks
- [x] Documentação de troubleshooting
- [x] Scripts de deploy e diagnóstico
- [x] Commit feito e seguro
- [x] Git push pronto

---

## 🎯 Próximos Passos

1. **Fazer push para GitHub:**
   ```bash
   git push origin main
   ```

2. **Deploy no servidor:**
   ```bash
   ssh pedropoiani@192.168.1.45 "cd simplescaixa && bash deploy.sh"
   ```

3. **Testar:**
   ```bash
   curl http://192.168.1.45:5000/health
   ```

4. **Monitorar logs:**
   ```bash
   ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose logs -f web"
   ```

---

## ⚙️ Mudanças Técnicas Detalhadas

### app/__init__.py
```python
# Novo: importar text() do SQLAlchemy
from sqlalchemy import text

# Novo: Health check endpoint
@app.route('/health')
def health():
    try:
        from app.models import db
        db.session.execute(text('SELECT 1'))
        return {'status': 'ok', 'db': 'connected'}, 200
    except Exception as e:
        return {'status': 'degraded', 'db': 'disconnected'}, 503
```

### docker-compose.yml
```yaml
# Novo: depends_on com condition
depends_on:
  db:
    condition: service_healthy

# Novo: healthcheck para web
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Novo: healthcheck para db
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U pdvuser -d pdvmf"]
  interval: 10s
  timeout: 5s
  retries: 5
```

### Dockerfile
```dockerfile
# Novo: instalar curl
RUN apt-get install -y curl

# Novo: healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```

---

Pronto! Site deve estar funcionando agora. 🎉
