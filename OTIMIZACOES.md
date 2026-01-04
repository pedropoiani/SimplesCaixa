# ⚡ Otimizações e Melhorias

## Performance

### 1. Configurar Cache (Redis)

Adicione ao `requirements.txt`:
```
flask-caching==2.1.0
redis==5.0.1
```

Adicione ao `app/__init__.py`:
```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
cache.init_app(app)
```

No `docker-compose.yml`, adicione:
```yaml
  redis:
    image: redis:7-alpine
    restart: unless-stopped
```

### 2. Compressão GZIP

Adicione ao `app/__init__.py`:
```python
from flask_compress import Compress

Compress(app)
```

No `requirements.txt`:
```
flask-compress==1.14
```

### 3. Otimizar Queries do Banco

Use eager loading:
```python
from sqlalchemy.orm import joinedload

lancamentos = Lancamento.query.options(
    joinedload(Lancamento.caixa)
).filter_by(caixa_id=caixa_id).all()
```

---

## Segurança

### 1. Limitar Taxa de Requisições

Adicione ao `requirements.txt`:
```
flask-limiter==3.5.0
```

No `app/__init__.py`:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

Nas rotas:
```python
@api_bp.route('/lancamento', methods=['POST'])
@limiter.limit("10 per minute")
def criar_lancamento():
    # ...
```

### 2. Adicionar Autenticação

Crie modelo de usuário em `app/models.py`:
```python
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

Instale Flask-Login:
```bash
pip install flask-login
```

Configure em `app/__init__.py`:
```python
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))
```

Proteja as rotas:
```python
from flask_login import login_required, current_user

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')
```

### 3. CSRF Protection

```bash
pip install flask-wtf
```

No `app/__init__.py`:
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

---

## Features Extras

### 1. Impressão de Cupom (PDF)

```bash
pip install reportlab
```

Adicione rota em `app/routes.py`:
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

@api_bp.route('/caixa/<int:id>/relatorio-pdf', methods=['GET'])
def gerar_pdf_caixa(id):
    caixa = Caixa.query.get_or_404(id)
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Adicionar conteúdo
    p.drawString(100, 800, f"Relatório do Caixa #{caixa.id}")
    # ... mais conteúdo
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'caixa_{caixa.id}.pdf'
    )
```

### 2. Envio de Email (Relatórios)

```bash
pip install flask-mail
```

Configure:
```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mail = Mail(app)

# Enviar relatório
def enviar_relatorio_fechamento(caixa):
    msg = Message(
        f'Fechamento do Caixa #{caixa.id}',
        sender='noreply@seupdv.com',
        recipients=['admin@seupdv.com']
    )
    msg.body = f'''
    Caixa fechado em {caixa.data_fechamento}
    Saldo: R$ {caixa.saldo_atual}
    '''
    mail.send(msg)
```

### 3. Dashboard com Gráficos

Instale Chart.js (via CDN no HTML):
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

Adicione rota para dados:
```python
@api_bp.route('/dashboard/grafico-vendas', methods=['GET'])
def grafico_vendas():
    # Últimos 7 dias
    dias = []
    valores = []
    
    for i in range(7, -1, -1):
        data = datetime.now() - timedelta(days=i)
        inicio = data.replace(hour=0, minute=0, second=0)
        fim = data.replace(hour=23, minute=59, second=59)
        
        total = db.session.query(func.sum(Lancamento.valor)).filter(
            and_(
                Lancamento.tipo == 'entrada',
                Lancamento.categoria == 'venda',
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).scalar() or 0
        
        dias.append(data.strftime('%d/%m'))
        valores.append(float(total))
    
    return jsonify({
        'labels': dias,
        'valores': valores
    })
```

### 4. Notificações Push

Use service workers para notificações web:

Em `app/static/js/notifications.js`:
```javascript
// Pedir permissão
function solicitarPermissaoNotificacao() {
    if ('Notification' in window) {
        Notification.requestPermission();
    }
}

// Enviar notificação
function enviarNotificacao(titulo, mensagem) {
    if (Notification.permission === 'granted') {
        new Notification(titulo, {
            body: mensagem,
            icon: '/static/logo.png'
        });
    }
}

// Exemplo: notificar ao fechar caixa
enviarNotificacao('Caixa Fechado', 'Saldo: R$ 1.234,56');
```

### 5. Sincronização Multi-Loja

Adicione campo de loja:
```python
class Loja(db.Model):
    __tablename__ = 'loja'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    ativo = db.Column(db.Boolean, default=True)

# Adicione loja_id em Caixa e Lancamento
```

API de sincronização:
```python
@api_bp.route('/sync/enviar', methods=['POST'])
def sincronizar_dados():
    # Enviar dados para servidor central
    pass

@api_bp.route('/sync/receber', methods=['GET'])
def receber_dados():
    # Receber dados de outras lojas
    pass
```

---

## Monitoramento

### 1. Logs Estruturados

```bash
pip install python-json-logger
```

Configure:
```python
import logging
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
app.logger.addHandler(logHandler)
app.logger.setLevel(logging.INFO)
```

### 2. Sentry (Rastreamento de Erros)

```bash
pip install sentry-sdk[flask]
```

Configure:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="seu-dsn-aqui",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### 3. Health Check

```python
@main_bp.route('/health')
def health_check():
    try:
        # Testar banco de dados
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

---

## Testes

### Setup de Testes

Crie `tests/test_api.py`:
```python
import pytest
from app import create_app
from app.models import db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_abrir_caixa(client):
    response = client.post('/api/caixa/abrir', json={
        'operador': 'Teste',
        'troco_inicial': 100.00
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True

def test_criar_lancamento(client):
    # Primeiro abrir caixa
    client.post('/api/caixa/abrir', json={'troco_inicial': 100})
    
    # Criar lançamento
    response = client.post('/api/lancamento', json={
        'tipo': 'entrada',
        'categoria': 'venda',
        'valor': 50.00,
        'forma_pagamento': 'Dinheiro'
    })
    assert response.status_code == 200
```

Execute:
```bash
pip install pytest
pytest tests/
```

---

## Deploy Contínuo (CI/CD)

### GitHub Actions

Crie `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Render
      env:
        RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
      run: |
        curl -X POST https://api.render.com/v1/services/$SERVICE_ID/deploys \
          -H "Authorization: Bearer $RENDER_API_KEY"
```

---

## Melhorias de UX

### 1. PWA (Progressive Web App)

Crie `app/static/manifest.json`:
```json
{
  "name": "PDV-MF",
  "short_name": "PDV",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#2563eb",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```

Adicione ao `base.html`:
```html
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#2563eb">
```

### 2. Modo Offline

Use service workers para cache:
```javascript
// static/js/sw.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('pdv-v1').then((cache) => {
      return cache.addAll([
        '/',
        '/static/css/style.css',
        '/static/js/api.js'
      ]);
    })
  );
});
```

### 3. Dark Mode

Adicione CSS:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #1e293b;
    --card-bg: #0f172a;
    --text-primary: #f1f5f9;
  }
}
```

---

## Conclusão

Essas otimizações são opcionais mas podem melhorar muito:
- ✅ Performance
- ✅ Segurança
- ✅ Experiência do usuário
- ✅ Manutenibilidade

Implemente conforme necessário para seu caso de uso!
