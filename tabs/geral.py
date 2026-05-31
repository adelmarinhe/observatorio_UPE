import streamlit as st
import plotly.express as px
import utils

def generate_tab(df_filtro):
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
        df_evolucao = df_filtro.groupby("Mês/Ano")[utils.colunas_monetarias].sum().reset_index()
        df_evolucao = df_evolucao.sort_values("Mês/Ano")
        
        fig_1 = px.line(
            df_evolucao, 
            x="Mês/Ano", 
            y=utils.colunas_monetarias,
            labels=utils.nomes_atributos,
            color_discrete_sequence=["#ffffff", "#82cbff", "#0072c4"]
        )
        fig_1.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_1, use_container_width=True)

    with col1_2:
        st.markdown("**Distribuição por Fonte de Recurso**")
        df_fonte = df_filtro.groupby("fonte_recurso")["valor_total"].sum().reset_index()
        df_fonte = df_fonte.sort_values(by="valor_total", ascending=True)

        df_fonte["fr_curto"] = df_fonte["fonte_recurso"].apply(lambda x: str(x)[:25] + "..." if len(str(x)) > 25 else x)

        fig_2 = px.bar(
            df_fonte,
            x="valor_total",
            y="fr_curto",
            orientation="h",
            labels=utils.nomes_atributos,
            color="valor_total",
            color_continuous_scale="Blues"
        )
        fig_2.update_layout(coloraxis_showscale=False, yaxis={'type': 'category'})
        st.plotly_chart(fig_2, use_container_width=True)

    col2_1, col2_2 = st.columns(2)

    with col2_1:
        st.markdown("**Alocação Financeira por Ação**")
        df_bar_empilhado = df_filtro[df_filtro["valor_total"] > 0].copy()
        df_bar_empilhado["acao"] = df_bar_empilhado["acao"].fillna("Não Informado")
        
        df_grouped_bar_acao = df_bar_empilhado.groupby(["acao"])["valor_total"].sum().reset_index()
        df_grouped_bar_acao = df_grouped_bar_acao.sort_values(by="valor_total", ascending=True)

        df_grouped_bar_acao["acao_curto"] = df_grouped_bar_acao["acao"].apply(lambda x: str(x)[:25] + "..." if len(str(x)) > 25 else x)


        fig_3 = px.bar(
            df_grouped_bar_acao,
            x="valor_total",
            y="acao_curto",
            orientation="h",
            labels=utils.nomes_atributos,
            color_continuous_scale="Blues"
        )
        fig_3.update_layout(barmode="stack", yaxis={'categoryorder': 'total ascending'}, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_3, use_container_width=True)

    with col2_2:
        st.markdown("**Alocação Financeira por Função**")
        df_bar_empilhado_funcao = df_filtro[df_filtro["valor_total"] > 0].copy()
        df_bar_empilhado_funcao["funcao"] = df_bar_empilhado_funcao["funcao"].fillna("Não Informado")
        
        df_grouped_bar_funcao = df_bar_empilhado_funcao.groupby(["funcao"])["valor_total"].sum().reset_index()
        df_grouped_bar_funcao = df_grouped_bar_funcao.sort_values(by="valor_total", ascending=True)

        fig_4 = px.bar(
            df_grouped_bar_funcao,
            x="valor_total",
            y="funcao",
            orientation="h",
            labels=utils.nomes_atributos,
            color_continuous_scale="Blues"
        )
        fig_4.update_layout(barmode="stack", yaxis={'categoryorder': 'total ascending'}, legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_4, use_container_width=True)

