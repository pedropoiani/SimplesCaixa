# 🌐 PDV-MF Web - Sistema de Caixa Online

Sistema completo de Ponto de Venda com Controle de Caixa desenvolvido em Python Flask + Web moderna.

## ✨ Características

- ✅ **Interface Web Responsiva** - Funciona em desktop, tablet e mobile
- ✅ **Backend em Flask** - API REST robusta e escalável
- ✅ **Banco de Dados Flexível** - SQLite (local) ou PostgreSQL (produção)
- ✅ **Controle completo de caixa** - Abertura, lançamentos e fechamento
- ✅ **Cálculo automático de troco** - Para vendas em dinheiro
- ✅ **Múltiplas formas de pagamento** - Configurável
- ✅ **Histórico e relatórios** - Com filtros e exportação CSV
- ✅ **Painel em tempo real** - Resumo financeiro atualizado
- ✅ **Docker Ready** - Fácil deploy em containers

## 🚀 Instalação Local

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

```bash
# 1. Navegue até a pasta do projeto
cd ~/Downloads/SimplesCaixa

# 2. Crie um ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env se necessário

# 5. Execute a aplicação
python run.py
```

A aplicação estará disponível em: http://localhost:5000

## 🐳 Executar com Docker

### Apenas a aplicação (SQLite)

```bash
# Build da imagem
docker build -t pdv-mf .

# Executar
docker run -p 5000:5000 -v $(pwd)/data:/app/data pdv-mf
```

### Aplicação + PostgreSQL

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar os serviços
docker-compose down
```

## 💰 Opções de Hospedagem (Preço Bom)

### 1. 🟢 **Render.com** (RECOMENDADO - GRÁTIS)

**Preço:** GRATUITO (com limitações) ou $7/mês (hobby)
**Vantagens:**
- Deploy automático via Git
- SSL gratuito
- PostgreSQL incluído (grátis)
- Fácil configuração
- Acordado automaticamente quando acessado

**Como Hospedar:**

1. Crie uma conta em https://render.com
2. Conecte seu repositório Git
3. Crie um novo "Web Service":
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT run:app`
4. Adicione um PostgreSQL (gratuito)
5. Configure as variáveis de ambiente:
   - `SECRET_KEY`: gere uma chave aleatória
   - `DATABASE_URL`: será preenchido automaticamente pelo PostgreSQL
   - `FLASK_ENV`: production

**Limitações do plano gratuito:**
- Dorme após 15 minutos de inatividade
- Leva ~30 segundos para acordar no primeiro acesso
- 750 horas/mês grátis

---

### 2. 🔵 **Railway.app** (MUITO FÁCIL - $5/mês)

**Preço:** $5/mês (com créditos iniciais grátis)
**Vantagens:**
- Deploy extremamente simples
- PostgreSQL incluído
- SSL automático
- Sem sleep/acordar
- Muito rápido

**Como Hospedar:**

1. Acesse https://railway.app
2. Clique em "Start a New Project"
3. Escolha "Deploy from GitHub repo"
4. Selecione seu repositório
5. Railway detecta automaticamente o Flask
6. Adicione PostgreSQL:
   - Clique em "+ New" → "Database" → "PostgreSQL"
7. As variáveis de ambiente são configuradas automaticamente

**Custo estimado:** $5-10/mês dependendo do uso

---

### 3. 🟣 **Heroku** (CLÁSSICO - Grátis acabou, mas vale a pena)

**Preço:** $7/mês (Eco Dynos) ou $25/mês (Basic)
**Vantagens:**
- Plataforma madura e confiável
- Muitos add-ons disponíveis
- Boa documentação
- PostgreSQL fácil de adicionar

**Como Hospedar:**

1. Instale Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli
2. Execute os comandos:

```bash
# Login
heroku login

# Criar app
heroku create seu-pdv-mf

# Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# Configurar variáveis
heroku config:set SECRET_KEY=sua-chave-secreta
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Abrir aplicação
heroku open
```

**Custo:** $7/mês (Eco) - não dorme, mas pode ter delay no primeiro acesso

---

### 4. 🟠 **Fly.io** (MODERNO - Grátis com limites)

**Preço:** Grátis (com limites) ou ~$3-5/mês
**Vantagens:**
- Deploy global (edge computing)
- Muito rápido
- SSL automático
- PostgreSQL gratuito (com limites)

**Como Hospedar:**

1. Instale Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Execute:

```bash
# Login
fly auth login

# Inicializar
fly launch

# Deploy
fly deploy

# Ver logs
fly logs
```

**Plano gratuito:**
- 3 VMs compartilhadas
- 160GB de tráfego/mês
- PostgreSQL 3GB

---

### 5. 💚 **PythonAnywhere** (ESPECIALIZADO - $5/mês)

**Preço:** Grátis (limitado) ou $5/mês
**Vantagens:**
- Especializado em Python
- Muito fácil de configurar
- MySQL incluído
- Boa para iniciantes

**Como Hospedar:**

1. Crie conta em https://www.pythonanywhere.com
2. Vá em "Web" → "Add a new web app"
3. Escolha Flask
4. Upload dos arquivos via interface web ou Git
5. Configure o WSGI file
6. Configure variáveis de ambiente

**Plano $5/mês:**
- SSL customizado
- Domínio próprio
- Mais recursos

---

### 6. 🐳 **VPS (Mais Controle) - A partir de R$ 10/mês**

Se você quer mais controle e recursos, considere um VPS:

#### **Contabo** (Alemanha) - R$ 20/mês
- 4 vCPU, 8GB RAM, 200GB SSD
- Melhor custo-benefício
- https://contabo.com

#### **Hetzner** (Alemanha) - R$ 25/mês
- 2 vCPU, 4GB RAM, 40GB SSD
- Excelente reputação
- https://www.hetzner.com

#### **DigitalOcean** (Global) - $6/mês (R$ 30)
- 1 vCPU, 1GB RAM, 25GB SSD
- Muito fácil de usar
- https://www.digitalocean.com

#### **Vultr** (Global) - $6/mês (R$ 30)
- Similar ao DigitalOcean
- Boa performance
- https://www.vultr.com

#### **Oracle Cloud** (GRÁTIS para sempre!)
- 4 vCPU ARM, 24GB RAM grátis PARA SEMPRE
- 200GB storage
- Excelente para quem quer economia máxima
- https://www.oracle.com/cloud/free/

**Para VPS, você precisa:**

```bash
# 1. Conectar via SSH
ssh root@seu-servidor

# 2. Instalar Docker
curl -fsSL https://get.docker.com | sh

# 3. Clonar repositório
git clone https://github.com/seu-usuario/pdv-mf.git
cd pdv-mf

# 4. Configurar variáveis
nano .env

# 5. Executar com Docker Compose
docker-compose up -d

# 6. (Opcional) Configurar Nginx como proxy reverso
# Ver seção "Configuração de Produção" abaixo
```

---

## 🏆 Comparativo de Preços

| Plataforma | Preço/Mês | Melhor Para | Dificuldade |
|------------|-----------|-------------|-------------|
| **Render** | Grátis* | Teste/Pequeno uso | ⭐ Fácil |
| **Oracle Cloud** | Grátis | Economia máxima | ⭐⭐⭐ Médio |
| **Railway** | $5 | Facilidade | ⭐ Muito Fácil |
| **PythonAnywhere** | $5 | Python focus | ⭐ Fácil |
| **Heroku** | $7 | Confiabilidade | ⭐⭐ Fácil |
| **Contabo VPS** | R$ 20 | Melhor custo-benefício | ⭐⭐⭐ Avançado |
| **Hetzner VPS** | R$ 25 | Performance | ⭐⭐⭐ Avançado |

*Com limitações (dorme após inatividade)

---

## 🎯 Nossa Recomendação

### Para Começar (Grátis)
1. **Render.com** - Melhor opção gratuita para começar
2. **Oracle Cloud** - Se quiser algo permanente e gratuito (mais técnico)

### Para Produção (Pago)
1. **Railway** ($5) - Mais fácil e confiável
2. **Contabo VPS** (R$ 20) - Melhor custo-benefício com mais recursos

---

## ⚙️ Configuração de Produção

### Variáveis de Ambiente Necessárias

```bash
SECRET_KEY=sua-chave-aleatoria-aqui-deve-ser-longa-e-segura
DATABASE_URL=postgresql://usuario:senha@host:5432/database
FLASK_ENV=production
PORT=5000
```

### Gerar Secret Key Segura

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Usando PostgreSQL

Se você escolher usar PostgreSQL ao invés de SQLite:

1. A maioria das plataformas oferece PostgreSQL gerenciado
2. A conexão é automática via variável `DATABASE_URL`
3. Não precisa fazer nada além de configurar a variável

---

## 📁 Estrutura do Projeto

```
SimplesCaixa/
├── app/
│   ├── __init__.py           # Inicialização Flask
│   ├── models.py             # Modelos do banco de dados
│   ├── routes.py             # Rotas da API
│   ├── templates/            # Templates HTML
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── historico.html
│   │   └── configuracoes.html
│   └── static/               # Arquivos estáticos
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── api.js
│           ├── utils.js
│           ├── caixa.js
│           ├── historico.js
│           └── configuracoes.js
├── run.py                    # Arquivo principal
├── requirements.txt          # Dependências Python
├── Dockerfile               # Configuração Docker
├── docker-compose.yml       # Docker Compose
├── .env.example             # Exemplo de variáveis
├── .gitignore              # Arquivos ignorados pelo Git
└── README.md               # Este arquivo
```

---

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar em modo debug
python run.py

# Ou com Flask CLI
flask run --debug
```

### Docker

```bash
# Build
docker build -t pdv-mf .

# Run
docker run -p 5000:5000 pdv-mf

# Com Docker Compose
docker-compose up -d        # Iniciar
docker-compose logs -f      # Ver logs
docker-compose down         # Parar
docker-compose restart      # Reiniciar
```

---

## 🌐 Acessando a Aplicação

Após o deploy, você terá:

- **Painel de Caixa:** `/` - Abertura, lançamentos e painel
- **Histórico:** `/historico` - Consultas e relatórios
- **Configurações:** `/configuracoes` - Configurar loja e formas de pagamento

---

## 🔒 Segurança

### Importante em Produção:

1. **Mude o SECRET_KEY** - Nunca use o padrão
2. **Use HTTPS** - Todas as plataformas oferecem SSL gratuito
3. **PostgreSQL** - Prefira ao SQLite em produção
4. **Backups** - Configure backups automáticos do banco
5. **Senhas fortes** - Para banco de dados

### Adicionar Autenticação (Opcional)

O sistema atualmente não tem login. Para adicionar:

1. Instale Flask-Login: `pip install flask-login`
2. Crie modelo de usuário
3. Adicione rotas de login/logout
4. Proteja as rotas com `@login_required`

Exemplo básico fornecido no código se necessário.

### ⚠️ Arquivos Sensíveis

**IMPORTANTE:** Nunca commite arquivos sensíveis para o GitHub!

O projeto já está configurado com `.gitignore` para proteger:
- ✅ `.env` - Variáveis de ambiente
- ✅ `*.db, *.sqlite` - Bancos de dados
- ✅ `*.pem, *.key` - Chaves e certificados
- ✅ `__pycache__/` - Cache Python
- ✅ `venv/` - Ambiente virtual
- ✅ `*.log` - Arquivos de log
- ✅ `instance/` - Dados da aplicação

**Antes de fazer commit, execute:**
```bash
./check_security.sh
```

📖 Veja [SEGURANCA.md](SEGURANCA.md) para mais detalhes sobre segurança.

---

## 📱 Mobile

A interface é totalmente responsiva e funciona em:
- 📱 Smartphones
- 📟 Tablets
- 💻 Desktops

---

## 🐛 Problemas Comuns

### Erro de porta já em uso

```bash
# Mude a porta no .env
PORT=8000
```

### Banco de dados não cria tabelas

```bash
# Execute Python e crie manualmente
python
>>> from app import create_app
>>> from app.models import db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
```

### Erro de dependências

```bash
# Reinstale tudo
pip install --upgrade -r requirements.txt
```

---

## 📈 Próximas Melhorias

- [ ] Sistema de autenticação de usuários
- [ ] Impressão de cupons (PDF)
- [ ] Integração com impressoras térmicas
- [ ] App mobile nativo (React Native)
- [ ] Dashboard com gráficos
- [ ] Backup automático na nuvem
- [ ] Sincronização multi-loja
- [ ] API webhooks para integrações

---

## 📞 Suporte

Para problemas:
1. Verifique os logs da aplicação
2. Consulte este README
3. Verifique a documentação da plataforma de hospedagem

---

## 📄 Licença

Este software é fornecido "como está", sem garantias de qualquer tipo.

---

## 🎉 Pronto!

Seu sistema PDV agora está na web! 🚀

**Escolha a plataforma que melhor se adapta ao seu orçamento e necessidades.**

Para hospedagem **gratuita**: Use **Render.com**
Para **melhor custo-benefício pago**: Use **Railway** ($5) ou **Contabo VPS** (R$20)

Boa sorte! 💰💻
