FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretório para banco de dados (se usar SQLite)
RUN mkdir -p /app/data

# Variáveis de ambiente
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 5000

# Health check para Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Comando de inicialização com melhor tratamento de erros
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --access-logfile - --error-logfile - run:app"]
