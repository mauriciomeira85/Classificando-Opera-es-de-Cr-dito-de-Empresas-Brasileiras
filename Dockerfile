FROM python:3.10-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg2 \
    software-properties-common \
    && apt-get clean

# Instala o Java 8 manualmente
RUN mkdir -p /usr/lib/jvm && \
    wget https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u402-b06/OpenJDK8U-jdk_x64_linux_hotspot_8u402b06.tar.gz -O /tmp/jdk.tar.gz && \
    tar -xzf /tmp/jdk.tar.gz -C /usr/lib/jvm && \
    mv /usr/lib/jvm/jdk8u402-b06 /usr/lib/jvm/java-8-openjdk-amd64 && \
    rm /tmp/jdk.tar.gz

# Define variáveis de ambiente do Java
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Instala Streamlit e PySpark
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia os arquivos da aplicação
COPY . /app
WORKDIR /app

# Executa o app Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]

