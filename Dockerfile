# Imagem base com Java 11 e Debian Slim
FROM openjdk:11-slim

# Variáveis de ambiente
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=2.7
ENV JAVA_HOME=/usr/local/openjdk-11
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Instala dependências do sistema e Python
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    wget \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instala Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Define diretório da aplicação
WORKDIR /app

# Copia os arquivos da aplicação
COPY . /app

# Instala dependências do projeto
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expõe a porta da aplicação
EXPOSE 8501

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

