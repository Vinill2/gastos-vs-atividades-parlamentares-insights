FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY tasks/ tasks/
COPY tests/ tests/
COPY .env.example .env.example
COPY pytest.ini .
COPY README.md .

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PREFECT_HOME=/app/.prefect

# Criar diretório de dados
RUN mkdir -p data

# Executar o pipeline
CMD ["python", "tasks/main_prefect.py"]
