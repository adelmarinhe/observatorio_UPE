import streamlit as st
import plotly.express as px
import pandas as pd
import os

from tabs import credores, empenhos, geral, ficha_credor
from scripts import tratamento, filtros
import utils, config

# CONFIGURAÇÃO DA PÁGINA 
# st.set_page_config(page_title="UPE - Despesas Governamentais", page_icon="🏛️", layout="wide")

config.config("UPE - Despesas Governamentais")
st.title("Dashboard de Despesas da Pró-Reitoria de Administração e Finanças da UPE")
st.markdown("Análise da execução orçamentária e fornecedores baseada nos dados de despesas gerais do Portal da Transparência do Governo de Pernambuco.")

# CARREGAMENTO DE DADOS 
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, sep=",", encoding="utf-8")
    return df

fl = st.file_uploader("Upload da planilha de Despesas (CSV)", type=["csv"])

if fl is not None:
    df = load_data(fl)
else:
    st.info("Aguardando upload do arquivo CSV. Carregando dados de exemplo locais (se disponíveis)...")
    try:
        df = load_data("arquivos_concatenados.csv")
    except FileNotFoundError:
        st.warning("Nenhum arquivo carregado e arquivo local não encontrado.")
        st.stop()

# TRATAMENTO DE DADOS 
df = tratamento.treat_dates(df)
df = tratamento.treat_values(df, utils.colunas_monetarias)

# FILTROS LATERAIS (GLOBAIS) 
with st.sidebar:
    # Você pode usar um link da web ou um arquivo local (ex: "imagens/logo_upe.png")
    st.image("images/upe_logo-removebg-preview.png", use_container_width=True)
    st.markdown("**Pró-Reitoria de Adminstração e Finanças** \nPROADMI - Financeiro", text_alignment='center')
    st.divider()
    st.header("Filtros Globais")

df_filtro = filtros.gerar_filtros(df)

# ABAS DO DASHBOARD 
tab_1, tab_2, tab_3, tab_4 = st.tabs(["Gestão Executiva e Orçamentária", "Empenhos", "Credores", "Ficha Individual do Credor"])

# ABA 1: GESTÃO EXECUTIVA 
with tab_1:
    geral.generate_tab(df_filtro)   

# ABA 2: EMPENHOS
with tab_2:
    empenhos.generate_tab(df_filtro)

# ABA 3: FORNECEDORES E CONTRATAÇÕES 
with tab_3:
    credores.generate_tab(df_filtro)

# ABA 4: FICHA INDIVIDUAL DO CREDOR
with tab_4:
    ficha_credor.generate_profile(df_filtro)

# TABELA DE DADOS & DOWNLOAD 
st.divider()
with st.expander("Tabela de Dados Brutos"):
    st.dataframe(df_filtro)

    csv = df_filtro.to_csv(index=False, sep=";").encode("utf-8")
    st.download_button(
        label="Baixar dados filtrados (CSV)",
        data=csv,
        file_name="despesas_upe_filtradas.csv",
        mime="text/csv"
    )