# 🚀 Guia de Deploy - SimplesCaixa

## 📋 Resumo do Projeto

**SimplesCaixa** é um **Sistema de PDV (Ponto de Venda) Multi-Funcional** construído com:
- **Backend**: Python (Flask)
- **Frontend**: HTML5 + CSS3 + JavaScript (ES5/ES6+)
- **Banco de Dados**: PostgreSQL (Docker)
- **Deployment**: Docker Compose
- **Server**: 192.168.1.45 (pedropoiani@)

---

## 🔧 Stack Técnico

### Backend
- Python 3.x + Flask
- SQLAlchemy ORM
- PostgreSQL 15
- Push Notifications (Web Push API)
- PDF Generator

### Frontend
- HTML5 Responsivo
- CSS3 com gradientes/flexbox
- JavaScript (ES5 compatível com iOS 9+)
- Service Workers (Progressive Web App)
- Emojis como ícones

### DevOps
- Docker + Docker Compose
- Volume persistence para banco de dados
- Cloudflare Tunnel (opcional)

---

## 📂 Estrutura do Projeto

```
SimplesCaixa/
├── app/
│   ├── __init__.py           # Inicialização Flask
│   ├── models.py             # ORM (SQLAlchemy)
│   ├── routes.py             # Rotas API
│   ├── pdf_generator.py      # Geração de PDFs
│   ├── push_notifications.py # Web Push
│   ├── templates/
│   │   ├── base.html         # Layout base (com polyfills ES5)
│   │   ├── index.html        # Caixa
│   │   ├── historico.html    # Histórico
│   │   ├── configuracoes.html # Configurações
│   │   └── gerente.html      # Painel gerente
│   └── static/
│       ├── css/style.css     # Estilos
│       ├── js/
│       │   ├── api.js        # Cliente API
│       │   ├── utils.js      # Funções utilitárias
│       │   ├── caixa.js      # Lógica do PDV
│       │   ├── historico.js  # Histórico
│       │   ├── configuracoes.js
│       │   └── sw.js         # Service Worker
│       └── img/              # Imagens
├── docker-compose.yml        # Orquestração de containers
├── Dockerfile                # Build da aplicação
├── requirements.txt          # Dependências Python
├── run.py                    # Entrypoint da aplicação
├── start.sh                  # Script de inicialização
├── setup-server.sh           # Setup inicial do servidor
└── .env                      # Variáveis de ambiente (gitignore)
```

---

## 🚀 Deploy via SSH

### Acesso
```bash
ssh pedropoiani@192.168.1.45
```

### Caminho do Projeto
```bash
/home/pedropoiani/simplescaixa
```

### Comando de Deploy (Pull + Rebuild)
```bash
cd /home/pedropoiani/simplescaixa && \
git pull origin main && \
bash deploy.sh
```

### Verificar Status
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose ps"
```

### Verificar Saúde
```bash
curl http://192.168.1.45:5000/health
```

### Ver Logs
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose logs -f web"
```

---

## 🔌 Endpoints da API

### Caixa
- `GET /api/caixa/status` - Status atual do caixa
- `POST /api/caixa/abrir` - Abrir caixa
- `POST /api/caixa/fechar` - Fechar caixa
- `GET /api/caixa/painel` - Painel de controle

### Lançamentos
- `POST /api/lancamento` - Criar lançamento
- `DELETE /api/lancamento/{id}` - Deletar lançamento
- `GET /api/lancamentos` - Listar lançamentos

### Configuração
- `GET /api/configuracao` - Obter configurações
- `PUT /api/configuracao` - Atualizar configurações

### Relatórios
- `GET /api/relatorio/resumo` - Resumo do período

---

## 🔐 Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://pdvuser:pdvpass@db:5432/pdvmf
SECRET_KEY=sua-chave-secreta-muito-longa-aqui
FLASK_ENV=production
VAPID_PUBLIC_KEY=sua-chave-publica-aqui
VAPID_PRIVATE_KEY=sua-chave-privada-aqui
```

---

## 📦 Inicializar Servidor (Primeira Vez)

```bash
ssh pedropoiani@192.168.1.45
cd simplescaixa
bash setup-server.sh  # Executa setup completo
docker-compose up -d  # Inicia containers em background
```

---

## 🔄 Processo de Deploy

### Local (Seu Computador)
1. Fazer alterações no código
2. Commit e push para GitHub:
   ```bash
   git add -A
   git commit -m "Descrição da mudança"
   git push origin main
   ```

### Servidor (192.168.1.45)
A mudança é refletida com:
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && git pull origin main && docker-compose restart web"
```

**Tempo**: ~5-10 segundos

---

## ⚙️ Manutenção

### Rebuild da imagem Docker
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose up -d --build"
```

### Limpar dados antigos
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose down -v"
```

### Backup do banco de dados
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose exec db pg_dump -U pdvuser pdvmf > backup_$(date +%Y%m%d_%H%M%S).sql"
```

---

## 🐛 Troubleshooting

### Container não inicia
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose logs web"
```

### Banco de dados corrompido
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose down -v && docker-compose up -d"
```

### Reset completo
```bash
ssh pedropoiani@192.168.1.45 "cd simplescaixa && docker-compose down && git reset --hard origin/main && docker-compose up -d --build"
```

---

## 📱 Compatibilidade

- ✅ Chrome/Firefox (moderno)
- ✅ Safari iOS 9+ (com polyfills ES5)
- ✅ Edge (moderno)
- ✅ Navegadores antigos (ES5)

---

## 📊 Features

### PDV (Ponto de Venda)
- Teclado virtual numérico
- Cálculo automático de troco
- Múltiplas formas de pagamento
- Abrir/fechar caixa

### Histórico
- Filtros por período, tipo, categoria
- Exportar para CSV
- Detalhes de cada caixa

### Gerente
- Painel executivo
- Relatórios
- Configurações

### Notificações
- Push notifications (Web Push API)
- Sincronização offline
- Service Worker

---

## 🔗 Links Úteis

- **Repositório**: https://github.com/pedropoiani/SimplesCaixa
- **Servidor**: http://192.168.1.45:5000 (ou via Cloudflare Tunnel)
- **Documentação Flask**: https://flask.palletsprojects.com/

---

## 📝 Última Atualização

**Data**: 9 de janeiro de 2026  
**Mudança**: Adição de polyfills ES5 para compatibilidade com iOS 9

---

**Mantém este arquivo atualizado após alterações significativas no projeto.**
