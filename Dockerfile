# Imagem base
FROM python:3.10-slim

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-11-jdk-headless \
    wget \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente Java e Spark
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_VERSION=3.3.2
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# Instalar o Spark
RUN mkdir -p /opt && \
    curl -L https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    | tar -xz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

# Copiar arquivos do app
WORKDIR /app
COPY . /app

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Executar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

