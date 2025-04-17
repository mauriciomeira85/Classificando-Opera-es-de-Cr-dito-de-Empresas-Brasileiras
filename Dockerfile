# Imagem base com Java 8 já instalado
FROM openjdk:8-slim

# Variáveis de ambiente
ENV PYSPARK_PYTHON=python3
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=2.7
ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala o Spark compatível
RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Copia os arquivos da aplicação
WORKDIR /app
COPY . .

# Instala dependências Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Executa a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

