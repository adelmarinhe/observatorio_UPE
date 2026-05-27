import streamlit as st
import plotly.express as px
import pandas as pd
import os

from tabs import empenhos, geral, fornecedores, acao_funcao
from scripts import tratamento

# CONFIGURAÇÃO DA PÁGINA 
st.set_page_config(page_title="UPE - Despesas Governamentais", page_icon="🏛️", layout="wide")

st.title("UPE - Dashboard de Despesas Públicas")
st.markdown("Análise da execução orçamentária e fornecedores baseada nos dados do e-Fisco.")

# CARREGAMENTO DE DADOS 
@st.cache_data
def load_data(file):
    # Lendo o CSV delimitado por ponto e vírgula
    df = pd.read_csv(file, sep=",", encoding="utf-8")
    return df

fl = st.file_uploader("Upload da planilha de Despesas (CSV)", type=["csv"])

if fl is not None:
    df = load_data(fl)
else:
    # Caso não faça upload, tenta ler um arquivo local (ajuste o caminho se necessário)
    st.info("Aguardando upload do arquivo CSV. Carregando dados de exemplo locais (se disponíveis)...")
    try:
        df = load_data("arquivos_concatenados.csv")
    except FileNotFoundError:
        st.warning("Nenhum arquivo carregado e arquivo local não encontrado.")
        st.stop()

# TRATAMENTO DE DADOS 
df = tratamento.treat_dates(df)
colunas_monetarias = ["valor_empenhado", "valor_liquidado", "valor_total"]
df = tratamento.treat_values(df, colunas_monetarias)

# FILTROS LATERAIS (GLOBAIS) 
st.sidebar.header("Filtros Globais")

anos_disponiveis = df["Ano"].dropna().unique().astype(int)
ano = st.sidebar.multiselect("Ano", sorted(anos_disponiveis, reverse=True))

unidades = st.sidebar.multiselect("Unidade Gestora", sorted(df["unidade_gestora"].dropna().unique()))
modalidades = st.sidebar.multiselect("Modalidade de Empenho", sorted(df["modalidade_empenho"].dropna().unique()))

# Aplicar filtros
df_filtro = df.copy()
if ano:
    df_filtro = df_filtro[df_filtro["Ano"].isin(ano)]
if unidades:
    df_filtro = df_filtro[df_filtro["unidade_gestora"].isin(unidades)]
if modalidades:
    df_filtro = df_filtro[df_filtro["modalidade_empenho"].isin(modalidades)]

# ABAS DO DASHBOARD 
tab_1, tab_2, tab_3 = st.tabs(["Gestão Executiva e Orçamentária", 
                                      "Empenhos",
                                      "Fornecedores e Contratações"])
#   tab_4 = "Alocação de Políticas Públicas"

# ABA 1: GESTÃO EXECUTIVA 
with tab_1:
    geral.generate_tab(df_filtro, colunas_monetarias)   

# ABA 2: EMPENHOS
with tab_2:
    empenhos.generate_tab(df_filtro)

# ABA 3: FORNECEDORES E CONTRATAÇÕES 
with tab_3:
    fornecedores.generate_tab(df_filtro)

# # ABA 4: Análise de Valores Empenhados por Ação e Função
# with tab_4:

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