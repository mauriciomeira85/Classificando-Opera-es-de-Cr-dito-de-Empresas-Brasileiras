import streamlit as st
import numpy as np
from datetime import datetime
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.feature import StringIndexer, OneHotEncoder, StandardScaler, VectorAssembler
from pyspark.sql import SparkSession, Row
from pyspark.ml import Pipeline
import os

os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/opt/spark"

# Inicializar a SparkSession
spark = SparkSession.builder \
    .appName("aplicacao_streamlit") \
    .config("spark.ui.enabled", "false") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.repl.eagerEval.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Caminho local para o modelo (ajustado corretamente)
base_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório do app.py
model_path = os.path.join(base_dir, "modelo_rf-20250408T233802Z-001", "modelo_rf")
modelo_rf = RandomForestClassificationModel.load(model_path)

# Interface Streamlit
st.title("🔍 Classificação de Risco de Crédito PJ")

with st.form("form_pj"):
    st.header("Informações da Empresa")

    # Inputs categóricos
    uf = st.selectbox("UF", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
    porte = st.selectbox("Porte", ["PJ - Micro", "PJ - Pequeno", "PJ - Médio", "PJ - Grande"])
    cnae_secao = st.selectbox("Setor CNAE", [
        "PJ - Comércio; reparação de veículos automotores e motocicletas",
        "PJ - Indústrias de transformação",
        "PJ - Agricultura, pecuária, produção florestal, pesca e aqüicultura"
    ])
    tcb = st.selectbox("Tipo de Crédito Bancário", ["Bancário", "Cooperativas", "Não bancário"])
    modalidade = st.selectbox("Modalidade", ["PJ - Capital de giro", "PJ - Rural e agroindustrial"])
    origem = st.selectbox("Origem do Crédito", ["Com destinação específica", "Sem destinação específica"])
    indexador = st.selectbox("Indexador", ["Pós-fixado", "Prefixado", "Índices de preços"])

    # Dados temporais
    data_base = st.date_input("Data Base", min_value=datetime(2012, 1, 1))
    dia_do_ano = data_base.timetuple().tm_yday
    mes = data_base.month
    ano = data_base.year
    trimestre = (mes - 1) // 3 + 1
    eh_fim_de_ano = 1 if mes == 12 else 0
    mes_sin = np.sin(2 * np.pi * mes / 12)
    mes_cos = np.cos(2 * np.pi * mes / 12)

    # Inputs numéricos
    numero_operacoes_int = st.number_input("Número de Operações Internas", min_value=0)
    a_vencer_ate_90_dias = st.number_input("A vencer até 90 dias (R$)", min_value=0.0)
    a_vencer_de_91_ate_360_dias = st.number_input("A vencer de 91 a 360 dias (R$)", min_value=0.0)
    a_vencer_acima_de_5400_dias = st.number_input("A vencer acima de 5400 dias (R$)", min_value=0.0)
    vencido_acima_de_15_dias = st.number_input("Vencido acima de 15 dias (R$)", min_value=0.0)
    carteira_ativa = st.number_input("Carteira Ativa (R$)", min_value=0.0)
    ativo_problematico = st.number_input("Ativo Problemático (R$)", min_value=0.0)

    submitted = st.form_submit_button("Prever Risco")

if submitted:
    # Criar DataFrame Spark com os dados
    input_data = {
        "dia_do_ano": dia_do_ano,
        "mes": mes,
        "ano": ano,
        "trimestre": trimestre,
        "eh_fim_de_ano": eh_fim_de_ano,
        "mes_sin": mes_sin,
        "mes_cos": mes_cos,
        "uf": uf,
        "tcb": tcb,
        "cnae_secao": cnae_secao,
        "porte": porte,
        "modalidade": modalidade,
        "origem": origem,
        "indexador": indexador,
        "numero_operacoes_int": numero_operacoes_int,
        "a_vencer_ate_90_dias": a_vencer_ate_90_dias,
        "a_vencer_de_91_ate_360_dias": a_vencer_de_91_ate_360_dias,
        "a_vencer_acima_de_5400_dias": a_vencer_acima_de_5400_dias,
        "vencido_acima_de_15_dias": vencido_acima_de_15_dias,
        "carteira_ativa": carteira_ativa,
        "ativo_problematico": ativo_problematico
    }

    df_input = spark.createDataFrame([Row(**input_data)])

    # Pré-processamento
    categorical_cols = ['uf', 'tcb', 'cnae_secao', 'porte', 'modalidade', 'origem', 'indexador']
    indexers = [StringIndexer(inputCol=col, outputCol=f"{col}_index", handleInvalid="keep") for col in categorical_cols]

    encoder = OneHotEncoder(
        inputCols=[f"{col}_index" for col in categorical_cols],
        outputCols=[f"{col}_encoded" for col in categorical_cols]
    )

    numeric_cols = [
        'dia_do_ano', 'mes', 'ano', 'trimestre', 'eh_fim_de_ano', 'mes_sin', 'mes_cos',
        'numero_operacoes_int', 'a_vencer_ate_90_dias', 'a_vencer_de_91_ate_360_dias',
        'a_vencer_acima_de_5400_dias', 'vencido_acima_de_15_dias', 'carteira_ativa', 'ativo_problematico'
    ]

    numeric_assembler = VectorAssembler(inputCols=numeric_cols, outputCol="numeric_features")
    scaler = StandardScaler(inputCol="numeric_features", outputCol="scaled_numeric_features")

    final_assembler = VectorAssembler(
        inputCols=[f"{col}_encoded" for col in categorical_cols] + ["scaled_numeric_features"],
        outputCol="features"
    )

    pipeline = Pipeline(stages=indexers + [encoder, numeric_assembler, scaler, final_assembler])
    df_input = pipeline.fit(df_input).transform(df_input)

    # Previsão
    predicao = modelo_rf.transform(df_input)
    risco = predicao.select("prediction").collect()[0][0]

    # Resultado
    st.subheader("Resultado")
    if risco == 0.0:
        st.success("✅ Baixo Risco")
    elif risco == 1.0:
        st.warning("⚠️ Médio Risco")
    else:
        st.error("❌ Alto Risco")

