# app.py
import streamlit as st
import numpy as np
from datetime import datetime
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.sql import SparkSession, Row
from pyspark.ml import PipelineModel
import os

# ❌ NÃO precisamos mais setar JAVA_HOME ou SPARK_HOME manualmente

# ✅ Inicializar SparkSession normalmente
spark = SparkSession.builder \
    .appName("aplicacao_streamlit") \
    .config("spark.ui.enabled", "false") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.repl.eagerEval.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# Caminho local para o modelo e pipeline
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "modelo_rf-20250408T233802Z-001", "modelo_rf")
pipeline_path = os.path.join(base_dir, "pipeline_model")

# Carregar modelo e pipeline
modelo_rf = RandomForestClassificationModel.load(model_path)
pipeline_model = PipelineModel.load(pipeline_path)

# Interface
st.title("🔍 Classificação de Risco de Crédito")
tipo_cliente = st.selectbox("Tipo de Cliente", ["PF - Pessoa Física", "PJ - Pessoa Jurídica"])

if tipo_cliente == "PJ - Pessoa Jurídica":
    with st.form("form_pj"):
        st.header("Informações da Empresa")

        # Categóricos
        porte = st.selectbox("Porte", ["PJ - Micro", "PJ - Pequeno", "PJ - Médio", "PJ - Grande"])
        cnae_secao = st.selectbox("Setor CNAE", [
            "PJ - Comércio; reparação de veículos automotores e motocicletas",
            "PJ - Indústrias de transformação",
            "PJ - Agricultura, pecuária, produção florestal, pesca e aqüicultura",
            "PJ - Atividades administrativas e serviços complementares",
            "PJ - Construção",
            "PJ - Transporte, armazenagem e correio",
            "PJ - Atividades profissionais, científicas e técnicas",
            "PJ - Saúde humana e serviços sociais",
            "PJ - Informação e comunicação",
            "PJ - Alojamento e alimentação",
            "PJ - Outras atividades de serviços",
            "PJ - Educação",
            "PJ - Atividades financeiras, de seguros e serviços relacionados",
            "PJ - Artes, cultura, esporte e recreação",
            "PJ - Atividades imobiliárias",
            "PJ - Água, esgoto, atividades de gestão de resíduos e descontaminação",
            "PJ - Indústrias extrativas",
            "PJ - Eletricidade e gás",
            "PJ - Administração pública, defesa e seguridade social",
            "PJ - Serviços domésticos",
            "PJ - Organismos internacionais e outras instituições extraterritoriais"
        ])
        cnae_subclasse = st.text_input("Subclasse CNAE (ex: 0111301, 4711301)")
        uf = st.selectbox("UF", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        tcb = st.selectbox("Tipo de Crédito Bancário", ["Bancário", "Cooperativas", "Não bancário"])
        modalidade = st.selectbox("Modalidade", [
            "PJ - Capital de giro",
            "PJ - Cheque especial e conta garantida",
            "PJ - Comércio exterior",
            "PJ - Financiamento de infraestrutura/desenvolvimento/projeto e outros créditos",
            "PJ - Habitacional",
            "PJ - Investimento",
            "PJ - Operações com recebíveis",
            "PJ - Outros créditos",
            "PJ - Rural e agroindustrial"
        ])
        origem = st.selectbox("Origem do Crédito", ["Com destinação específica", "Sem destinação específica"])
        indexador = st.selectbox("Indexador", ["Pós-fixado", "Prefixado", "Índices de preços", "Outros indexadores", "Flutuantes", "TCR/TRFC"])

        # Temporais
        data_base = st.date_input("Data Base", min_value=datetime(2012, 1, 1))
        dia_do_ano = data_base.timetuple().tm_yday
        mes = data_base.month
        ano = data_base.year
        trimestre = (mes - 1) // 3 + 1
        eh_fim_de_ano = 1 if mes == 12 else 0
        mes_sin = float(np.sin(2 * np.pi * mes / 12))
        mes_cos = float(np.cos(2 * np.pi * mes / 12))

        submitted = st.form_submit_button("Prever Risco")

    if submitted:
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
            "cnae_subclasse": cnae_subclasse,
            "porte": porte,
            "modalidade": modalidade,
            "origem": origem,
            "indexador": indexador,
            "numero_operacoes_int": 0,
            "a_vencer_ate_90_dias": 0.0,
            "a_vencer_de_91_ate_360_dias": 0.0,
            "a_vencer_acima_de_5400_dias": 0.0,
            "vencido_acima_de_15_dias": 0.0,
            "carteira_ativa": 0.0,
            "ativo_problematico": 0.0
        }

        df_input = spark.createDataFrame([Row(**input_data)])

        # Aplicar o pipeline treinado
        df_input = pipeline_model.transform(df_input)

        # Prever
        predicao = modelo_rf.transform(df_input)
        risco = predicao.select("prediction").collect()[0][0]

        st.subheader("Resultado")
        if risco == 0.0:
            st.success("✅ Baixo Risco")
        elif risco == 1.0:
            st.warning("⚠️ Médio Risco")
        else:
            st.error("❌ Alto Risco")

