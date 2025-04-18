import streamlit as st
import pandas as pd
import datetime
import joblib

# Carregar modelo treinado (substitua o caminho se necessário)
modelo = joblib.load("modelo_risco_credito.pkl")

# Função para prever o risco
def prever_risco(dados_input):
    df_input = pd.DataFrame([dados_input])
    pred = modelo.predict(df_input)[0]
    return pred

# Título e layout
st.set_page_config(page_title="Classificação de Risco de Crédito", layout="wide")

st.markdown(
    "<h1 style='display: flex; align-items: center;'>"
    "<img src='https://cdn-icons-png.flaticon.com/512/622/622669.png' width='40' style='margin-right: 10px;'>"
    "Classificação de Risco de Crédito para Empresas Brasileiras"
    "</h1>", 
    unsafe_allow_html=True
)

tipo_cliente = st.selectbox("Tipo de Cliente", ["PF - Pessoa Física", "PJ - Pessoa Jurídica"])

if tipo_cliente == "PF - Pessoa Física":
    st.warning("⚠️ Este sistema é destinado exclusivamente à análise de risco de crédito para **empresas (Pessoa Jurídica)**.")
else:
    st.markdown("### Informações da Empresa")
    col1, col2, col3 = st.columns(3)

    with col1:
        porte = st.selectbox("Porte", ["PJ - Micro", "PJ - Pequeno", "PJ - Médio", "PJ - Grande"])
    with col2:
        uf = st.selectbox("UF", ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
                                 "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
                                 "SE", "SP", "TO"])
    with col3:
        cnae_secao = st.selectbox("Setor CNAE", [
            "Agropecuária", "Indústrias extrativas", "Indústrias de transformação", 
            "Serviços", "Comércio; reparação de veículos", "Construção", 
            "Outras atividades de serviços", "Transporte; armazenagem", "Administração pública"
        ])

    st.markdown("### Dados Temporais e Financeiros")
    col4, col5 = st.columns(2)
    with col4:
        data_base = st.date_input("Data Base", datetime.date.today())
    with col5:
        tcb = st.selectbox("Tipo de Crédito", ["Bancário", "Mercado de Capitais", "Outros"])

    col6, col7 = st.columns(2)
    with col6:
        modalidade = st.selectbox("Modalidade", [
            "Capital de giro", "Cheque especial", "Conta garantida", 
            "Financiamento de máquinas", "Investimento", "Outros"
        ])
    with col7:
        origem = st.selectbox("Origem do Crédito", [
            "Com destinação específica", "Sem destinação específica"
        ])

    col8, col9 = st.columns(2)
    with col8:
        indexador = st.selectbox("Indexador", ["Pré-fixado", "Pós-fixado", "Híbrido"])
    with col9:
        numero_operacoes_int = st.number_input("Número de Operações", min_value=1, step=1, value=1)

    # Botão de previsão
    if st.button("Prever Risco de Crédito"):
        dados_input = {
            "porte": porte,
            "uf": uf,
            "cnae_secao": cnae_secao,
            "data_base": data_base,
            "tcb": tcb,
            "modalidade": modalidade,
            "origem": origem,
            "indexador": indexador,
            "numero_operacoes_int": numero_operacoes_int
        }

        risco = prever_risco(dados_input)

        st.success(f"🧠 Risco de Crédito Previsto: **{risco.upper()}**")

