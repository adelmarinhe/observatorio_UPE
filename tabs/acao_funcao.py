import streamlit as st
import plotly.express as px

def generate_tab(df_filtro):
    st.subheader("Análise de Valores Empenhados por Ação e Função")

    st.markdown("**Alocação Financeira por Ação e Subação**")
    df_bar_empilhado = df_filtro[df_filtro["valor_total"] > 0].copy()
    df_bar_empilhado["acao"] = df_bar_empilhado["acao"].fillna("Não Informado")
    df_bar_empilhado["subacao"] = df_bar_empilhado["subacao"].fillna("Não Informado")
    
    df_grouped_bar_acao = df_bar_empilhado.groupby(["acao", "subacao"])["valor_total"].sum().reset_index()
    df_grouped_bar_acao = df_grouped_bar_acao.sort_values(by="valor_total", ascending=True)

    fig_6 = px.bar(
        df_grouped_bar_acao,
        x="valor_total",
        y="acao",
        color="subacao",
        orientation="h",
        labels={"valor_total": "Valor Total (R$)", "acao": "Ação", "subacao": "Subação"},
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_6.update_layout(barmode="stack", yaxis={'categoryorder': 'total ascending'}, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_6, use_container_width=True)

    st.markdown("**Alocação Financeira por Função**")
    df_bar_empilhado_funcao = df_filtro[df_filtro["valor_total"] > 0].copy()
    df_bar_empilhado_funcao["funcao"] = df_bar_empilhado_funcao["funcao"].fillna("Não Informado")
    
    df_grouped_bar_funcao = df_bar_empilhado_funcao.groupby(["funcao"])["valor_total"].sum().reset_index()
    df_grouped_bar_funcao = df_grouped_bar_funcao.sort_values(by="valor_total", ascending=True)

    fig_7 = px.bar(
        df_grouped_bar_funcao,
        x="valor_total",
        y="funcao",
        orientation="h",
        labels={"valor_total": "Valor Total (R$)", "funcao": "Função"},
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_7.update_layout(barmode="stack", yaxis={'categoryorder': 'total ascending'}, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig_7, use_container_width=True)