# Dockerfile para IMUNOPREVINIVEIS
FROM python:3.11-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 streamlit && chown -R streamlit:streamlit /app
USER streamlit

# Expor porta
EXPOSE 8501

# Configurar Streamlit
RUN mkdir -p /home/streamlit/.streamlit
RUN echo "[server]\nheadless = true\nport = 8501\naddress = \"0.0.0.0\"\n[browser]\ngatherUsageStats = false" > /home/streamlit/.streamlit/config.toml

# Comando para executar
CMD ["streamlit", "run", "app/main.py"]
