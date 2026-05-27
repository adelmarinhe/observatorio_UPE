import streamlit as st
import plotly.express as px
import utils

def generate_tab(df_filtro, colunas_monetarias):
    st.subheader("Visão Macro da Execução do Orçamento")
    st.divider()
    
    total_empenhado = df_filtro["valor_empenhado"].sum()
    total_liquidado = df_filtro["valor_liquidado"].sum()
    total_pago = df_filtro["valor_total"].sum()
    indice_execucao = (total_liquidado / total_empenhado * 100) if total_empenhado > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Empenhado", f"R$ {(total_empenhado/(pow(10, 6))):,.2f} M")
    k2.metric("Total Liquidado", f"R$ {(total_liquidado/(pow(10, 6))):,.2f} M")
    k3.metric("Total Pago", f"R$ {(total_pago/(pow(10, 6))):,.2f} M")
    k4.metric("Índice de Execução", f"{indice_execucao:.1f}%")
    
    st.divider()
    col1_1, col1_2 = st.columns(2)
    
    with col1_1:
        st.markdown("**Evolução Mensal dos Gastos**")
        df_evolucao = df_filtro.groupby("Mês/Ano")[colunas_monetarias].sum().reset_index()
        df_evolucao = df_evolucao.sort_values("Mês/Ano")
        
        fig1 = px.line(
            df_evolucao, 
            x="Mês/Ano", 
            y=colunas_monetarias,
            labels=utils.nomes_atributos,
            color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c"]
        )
        fig1.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig1, use_container_width=True)

    with col1_2:
        st.markdown("**Distribuição por Fonte de Recurso**")
        df_fonte = df_filtro.groupby("fonte_recurso")["valor_total"].sum().reset_index()
        df_fonte = df_fonte.sort_values(by="valor_total", ascending=True)
        
        fig2 = px.bar(
            df_fonte,
            x="valor_total",
            y="fonte_recurso",
            orientation="h",
            labels=utils.nomes_atributos,
            color="valor_total",
            color_continuous_scale="Blues"
        )
        fig2.update_layout(coloraxis_showscale=False, yaxis={'type': 'category'})
        st.plotly_chart(fig2, use_container_width=True)