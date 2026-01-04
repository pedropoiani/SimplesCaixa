# 🚀 Guia Rápido de Início

## Rodar Local (Mais Simples)

```bash
# 1. Entre na pasta
cd ~/Downloads/SimplesCaixa

# 2. Instale as dependências
pip3 install -r requirements.txt

# 3. Execute
python3 run.py
```

Acesse: http://localhost:5000

---

## Deploy na Render.com (GRÁTIS)

### Passo 1: Prepare o Código

```bash
# Inicialize o Git (se ainda não tiver)
cd ~/Downloads/SimplesCaixa
git init
git add .
git commit -m "Sistema PDV-MF Web"
```

### Passo 2: Suba para o GitHub

1. Crie um repositório em https://github.com/new
2. Nomeie como `pdv-mf` ou similar
3. Execute:

```bash
git remote add origin https://github.com/SEU-USUARIO/pdv-mf.git
git branch -M main
git push -u origin main
```

### Passo 3: Deploy no Render

1. Acesse https://render.com e crie uma conta
2. Clique em **"New +"** → **"Web Service"**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name:** pdv-mf (ou outro nome)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT run:app`
   - **Instance Type:** Free

5. Clique em **"Advanced"** e adicione variáveis de ambiente:
   - `SECRET_KEY` = `sua-chave-aqui-gere-uma-random`
   - `FLASK_ENV` = `production`

6. Clique em **"Create Web Service"**

### Passo 4: Adicione PostgreSQL (Opcional mas recomendado)

1. No dashboard do Render, clique em **"New +"** → **"PostgreSQL"**
2. **Name:** pdv-mf-db
3. **Instance Type:** Free
4. Clique em **"Create Database"**
5. Copie a **External Database URL**
6. Volte no seu Web Service → Settings → Environment Variables
7. Adicione:
   - `DATABASE_URL` = cole a URL copiada

8. Salve e o Render fará o deploy automaticamente

### Pronto! 🎉

Seu sistema estará disponível em: `https://seu-app.onrender.com`

**Nota:** No plano gratuito, após 15 minutos de inatividade o app dorme e demora ~30 segundos para acordar no próximo acesso.

---

## Deploy na Railway (Mais Fácil - $5/mês)

### Muito mais simples:

1. Acesse https://railway.app
2. Clique em **"Start a New Project"**
3. Escolha **"Deploy from GitHub repo"**
4. Selecione seu repositório
5. Railway detecta tudo automaticamente
6. Adicione PostgreSQL:
   - Clique em **"+ New"** → **"Database"** → **"PostgreSQL"**
7. As variáveis de ambiente são configuradas automaticamente!

**Pronto!** Seu app estará no ar em menos de 5 minutos.

Railway oferece $5 de crédito grátis para testar.

---

## Configurações Importantes

### Gerar uma Secret Key Segura

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Use o resultado como `SECRET_KEY` nas variáveis de ambiente.

---

## Primeiro Acesso

1. Vá para `/configuracoes`
2. Configure:
   - Nome da loja
   - Responsável
   - Formas de pagamento
3. Salve
4. Volte para a página inicial
5. Clique em **"Abrir Caixa"**
6. Comece a usar!

---

## Custos Estimados

| Opção | Custo | Observação |
|-------|-------|------------|
| **Render Free** | R$ 0 | Dorme após 15 min |
| **Railway** | R$ 25 ($5) | Sempre ativo, muito fácil |
| **Heroku Eco** | R$ 35 ($7) | Confiável, pode ter delay |
| **VPS Contabo** | R$ 20 | Melhor custo-benefício, mais técnico |
| **Oracle Cloud** | R$ 0 | Grátis para sempre, mais difícil |

---

## Precisa de Ajuda?

1. Leia o README.md completo
2. Verifique os logs da plataforma
3. Teste localmente primeiro

Boa sorte! 🚀💰
