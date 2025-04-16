# Usa imagem com Java 11 já instalado
FROM openjdk:11

# Instala Python e pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Define diretório da aplicação
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . /app

# Instala dependências
RUN pip3 install --no-cache-dir -r requirements.txt

# Instala Spark (ajustado para versão usada no projeto)
ENV SPARK_VERSION=3.3.2
RUN curl -O https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    tar -xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop3 /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Configura variáveis de ambiente
ENV SPARK_HOME=/opt/spark
ENV PATH="$SPARK_HOME/bin:$PATH"
ENV JAVA_HOME=/usr/local/openjdk-11

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para iniciar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

