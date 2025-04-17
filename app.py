import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import os

# Configuração da página
st.set_page_config(page_title="Classificação de Risco de Crédito", layout="wide")
st.title("🔍 Classificação de Risco de Crédito para Empresas Brasileiras")

# Carregar o pipeline (pré-processamento + modelo)
@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "modelo_risco_credito.pkl")
    return joblib.load(model_path)

pipeline = load_model()

# Interface do usuário
tipo_cliente = st.selectbox("Tipo de Cliente", ["PF - Pessoa Física", "PJ - Pessoa Jurídica"])

if tipo_cliente == "PJ - Pessoa Jurídica":
    with st.form("form_pj"):
        st.header("Informações da Empresa")

        # Seção 1: Dados cadastrais
        col1, col2, col3 = st.columns(3)
        with col1:
            porte = st.selectbox("Porte", ["PJ - Micro", "PJ - Pequeno", "PJ - Médio", "PJ - Grande"])
            uf = st.selectbox("UF", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", 
                              "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
        with col2:
            cnae_secao = st.selectbox("Setor CNAE", [
                "Comércio; reparação de veículos",
                "Indústrias de transformação",
                "Agricultura, pecuária e pesca",
                "Atividades administrativas",
                "Construção",
                "Transporte e armazenagem"
            ])
            tcb = st.selectbox("Tipo de Crédito", ["Bancário", "Cooperativas", "Não bancário"])
        with col3:
            cnae_subclasse = st.text_input("Subclasse CNAE (ex: 0111301)", value="4711301")
            modalidade = st.selectbox("Modalidade", [
                "Capital de giro",
                "Cheque especial",
                "Comércio exterior",
                "Investimento",
                "Operações com recebíveis"
            ])

        # Seção 2: Dados temporais e financeiros
        st.subheader("Dados Temporais e Financeiros")
        col4, col5 = st.columns(2)
        with col4:
            data_base = st.date_input("Data Base", min_value=datetime(2012, 1, 1))
            origem = st.selectbox("Origem do Crédito", ["Com destinação específica", "Sem destinação específica"])
        with col5:
            indexador = st.selectbox("Indexador", ["Pós-fixado", "Prefixado", "Índices de preços", "Flutuantes"])
            numero_operacoes = st.number_input("Número de Operações", min_value=0, value=1)

        # Dados derivados (automáticos)
        dia_do_ano = data_base.timetuple().tm_yday
        mes = data_base.month
        ano = data_base.year
        trimestre = (mes - 1) // 3 + 1
        eh_fim_de_ano = 1 if mes == 12 else 0
        mes_sin = float(np.sin(2 * np.pi * mes / 12))
        mes_cos = float(np.cos(2 * np.pi * mes / 12))

        submitted = st.form_submit_button("Prever Risco de Crédito")

    if submitted:
        # Criar DataFrame de entrada
        input_data = {
            'dia_do_ano': dia_do_ano,
            'mes': mes,
            'ano': ano,
            'trimestre': trimestre,
            'eh_fim_de_ano': eh_fim_de_ano,
            'mes_sin': mes_sin,
            'mes_cos': mes_cos,
            'uf': uf,
            'tcb': tcb,
            'cnae_secao': cnae_secao,
            'cnae_subclasse': cnae_subclasse,
            'porte': porte,
            'modalidade': modalidade,
            'origem': origem,
            'indexador': indexador,
            'numero_operacoes_int': numero_operacoes,
            'a_vencer_ate_90_dias': 0.0,  # Valores padrão (ajustáveis conforme necessidade)
            'a_vencer_de_91_ate_360_dias': 0.0,
            'a_vencer_acima_de_5400_dias': 0.0,
            'vencido_acima_de_15_dias': 0.0,
            'carteira_ativa': 0.0,
            'ativo_problematico': 0.0
        }

        df_input = pd.DataFrame([input_data])

        # Fazer previsão
        risco = pipeline.predict(df_input)[0]

        # Exibir resultado
        st.subheader("Resultado da Classificação")
        if risco == 0.0:
            st.success("✅ **Baixo Risco** - Operação recomendada")
        elif risco == 1.0:
            st.warning("⚠️ **Médio Risco** - Analisar com cautela")
        else:
            st.error("❌ **Alto Risco** - Recomendamos não aprovar")

        # Mostrar features mais importantes (se o modelo for RandomForest)
        if hasattr(pipeline.named_steps['classificador'], 'feature_importances_'):
            st.subheader("Fatores mais relevantes para a decisão")
            importances = pipeline.named_steps['classificador'].feature_importances_
            features = pipeline[:-1].get_feature_names_out()  # Nomes das features após pré-processamento
            st.bar_chart(pd.Series(importances, index=features).sort_values(ascending=False).head(10))
