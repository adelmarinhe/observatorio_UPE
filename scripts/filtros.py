import streamlit as st

import pandas as pd


def gerar_filtros(df):
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

    return df_filtro