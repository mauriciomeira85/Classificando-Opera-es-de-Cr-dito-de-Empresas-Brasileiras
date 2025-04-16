# Etapa base com Python
FROM python:3.10-slim

# Variáveis de ambiente do Spark e Java
ENV PYSPARK_PYTHON=python3
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin

# Instala Java 11, curl, wget e outras dependências
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk \
    curl \
    wget \
    software-properties-common \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Spark 3.2.1 com Hadoop 2.7
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=hadoop2.7

RUN curl -L -o spark.tgz https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-${HADOOP_VERSION}.tgz && \
    tar -xvzf spark.tgz && \
    mv spark-${SPARK_VERSION}-bin-${HADOOP_VERSION} /opt/spark && \
    rm spark.tgz

# Copiar arquivos da aplicação para o container
WORKDIR /app
COPY . .

# Instalar dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

