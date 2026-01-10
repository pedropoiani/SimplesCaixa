# 🔧 Troubleshooting - Bad Gateway

## Problema: Status 502 Bad Gateway

### Causas Principais

1. **Flask não está respondendo** (port 5000)
2. **Banco de dados não conecta**
3. **Gunicorn crazeando**
4. **Timeout na inicialização**

---

## 🔍 Diagnóstico Passo a Passo

### 1. Verificar status dos containers

```bash
docker-compose ps
```

**Se algum container estiver `Exited` ou `Restarting`:**
```bash
docker-compose logs web
docker-compose logs db
```

### 2. Verificar saúde da aplicação

```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{"status": "ok", "db": "connected"}
```

**Se retornar erro:**
```bash
docker-compose logs web | grep -i error | tail -20
```

### 3. Verificar conexão com banco de dados

```bash
docker-compose exec db pg_isready -U pdvuser -d pdvmf
```

**Se falhar:** O PostgreSQL não está pronto ainda. Aguarde 30-60s.

### 4. Verificar porta 5000

```bash
netstat -tlnp | grep 5000
# ou
ss -tlnp | grep 5000
```

Deve estar em `LISTEN` e associada ao container.

---

## 🚀 Soluções Rápidas

### Solução 1: Reiniciar tudo (reset suave)

```bash
docker-compose restart
```

Aguarde 30-40 segundos para inicialização completa.

### Solução 2: Rebuild completo (reset duro)

```bash
docker-compose down
docker-compose up -d --build
```

### Solução 3: Limpar e reconstruir (reset muito duro)

```bash
docker-compose down -v  # Remove volumes também!
docker-compose up -d --build
```

**⚠️ AVISO: Isso deleta dados do banco!**

### Solução 4: Ver logs em tempo real

```bash
docker-compose logs -f web
```

Ctrl+C para sair.

---

## 📋 Checklist de Verificação

- [ ] `docker-compose ps` mostra containers em `Up` (não `Exited`)
- [ ] `curl http://localhost:5000/health` retorna status `ok`
- [ ] `docker-compose logs web` não mostra `ERROR` ou `CRITICAL`
- [ ] PostgreSQL iniciou com `database system is ready to accept connections`
- [ ] Porta 5000 está em `LISTEN`
- [ ] Arquivo `.env` existe com `DATABASE_URL` correto

---

## 🎯 Processo de Deploy Seguro

### Local (seu computador)

```bash
# 1. Fazer mudanças
git add -A
git commit -m "Fix: melhorar health check"

# 2. Testar localmente
docker-compose down
docker-compose up -d --build

# 3. Validar
sleep 30
curl http://localhost:5000/health

# 4. Push se OK
git push origin main
```

### Servidor (pedropoiani@192.168.1.45)

```bash
cd simplescaixa

# Opção A: Deploy automático
bash deploy.sh

# Opção B: Manual
git pull origin main
docker-compose down
docker-compose up -d --build
sleep 40
curl http://localhost:5000/health
```

---

## 🐛 Erros Específicos

### Erro: `connection refused`
**Causa:** Flask não está rodando na porta 5000
```bash
docker-compose logs web
```

### Erro: `FATAL: Ident authentication failed for user "pdvuser"`
**Causa:** PostgreSQL não consegue autenticar
```bash
# Verificar variáveis de ambiente
docker-compose exec web env | grep DATABASE_URL

# Deve ser: postgresql://pdvuser:pdvpass@db:5432/pdvmf
```

### Erro: `does not exist` (SQL error)
**Causa:** Tabelas não foram criadas
```bash
docker-compose down -v  # Delete tudo
docker-compose up -d --build
```

### Erro: `connection pool timeout`
**Causa:** Muitas conexões simultâneas
```bash
# Aumentar pool_size no código
```

---

## 📞 Contato

Se o problema persistir:

1. Coletar logs:
   ```bash
   docker-compose logs web > web.log
   docker-compose logs db > db.log
   ```

2. Enviar logs para análise

3. Verificar a data de última mudança:
   ```bash
   git log --oneline -5
   ```
