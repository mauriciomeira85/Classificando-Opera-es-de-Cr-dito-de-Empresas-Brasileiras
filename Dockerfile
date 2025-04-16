# Use uma imagem Debian mais completa com Python
FROM debian:bullseye

# Variáveis de ambiente
ENV PYTHON_VERSION=3.10
ENV SPARK_VERSION=3.2.1
ENV HADOOP_VERSION=2.7
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# Instalar dependências
RUN apt-get update && \
    apt-get install -y \
    openjdk-11-jdk \
    python3-pip \
    python3-dev \
    python3-venv \
    curl \
    wget \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Instalar Spark
RUN curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Copiar arquivos da aplicação
WORKDIR /app
COPY . /app

# Instalar pacotes Python
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

