# Usar imagem base com Java 8
FROM openjdk:8-slim

# Variáveis de ambiente
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3
ENV JAVA_HOME=/usr/local/openjdk-8
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=2.7
ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip curl wget bash ca-certificates gnupg software-properties-common && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Definir diretório da aplicação
WORKDIR /app

# Copiar arquivos da aplicação
COPY . .

# Instalar dependências do projeto
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

# Rodar aplicação
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

