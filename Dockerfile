# Usa imagem Python oficial
FROM python:3.10-slim

# Instala Java 8 e dependências do sistema
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk wget curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define variáveis de ambiente do Java
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Instala o Spark manualmente
ENV SPARK_VERSION=3.3.2
RUN wget https://downloads.apache.org/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz && \
    tar -xvzf spark-$SPARK_VERSION-bin-hadoop3.tgz && \
    mv spark-$SPARK_VERSION-bin-hadoop3 /opt/spark && \
    rm spark-$SPARK_VERSION-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$PATH"

# Cria diretório da aplicação
WORKDIR /app

# Copia todos os arquivos do projeto para o contêiner
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

