# Base com Java 11 já incluído
FROM openjdk:11-slim

# Instalar Python e dependências básicas
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv python3-dev \
    curl wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente
ENV PYSPARK_PYTHON=python3
ENV JAVA_HOME=/usr/local/openjdk-11
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

# Instalar Spark 3.2.1 + Hadoop 2.7
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=hadoop2.7

RUN curl -L -o spark.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}.tgz && \
    tar -xvzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-${HADOOP_VERSION} /opt/spark && \
    rm spark.tgz

# Copiar arquivos do projeto
WORKDIR /app
COPY . .

# Instalar dependências Python
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Porta default do Streamlit
EXPOSE 8501

# Comando de inicialização
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

