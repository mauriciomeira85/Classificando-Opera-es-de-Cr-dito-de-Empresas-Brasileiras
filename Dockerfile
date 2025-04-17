# Imagem base com Spark, Hadoop e Java já integrados
FROM jupyter/pyspark-notebook:spark-3.2.1

# Atualizar pacotes e instalar dependências do sistema
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget bash ca-certificates gnupg software-properties-common && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar a aplicação para o contêiner
WORKDIR /app
COPY . .

# Expõe a porta do Streamlit
EXPOSE 10000

# Rodar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

