import streamlit as st
import plotly.express as px


def generate_tab(df_filtro):
    st.subheader("Métricas de Empenhos Realizados")

    # Cálculos dos KPIs (Baseados na tabela já filtrada lateralmente)
    total_empenhado_filtrado = df_filtro['valor_empenhado'].sum()
    qtd_empenhos_filtrado = df_filtro.shape

    # Construção do layout de cartões
    k4_1, k4_2 = st.columns(2)
    k4_1.metric("Valor Total Empenhado (Filtro)", f"R$ {total_empenhado_filtrado:,.2f}")
    k4_2.metric("Quantidade Total de Empenhos", f"{qtd_empenhos_filtrado[0]}")

    # TODO: adicionar classificação por tipo de empenho

    st.divider()

    col4_graf1, col4_graf2 = st.columns(2)

    with col4_graf1:
        st.markdown("**Distribuição das Faixas de Valores Empenhados**")
        # Correção do filtro para usar os dados que respeitam o painel lateral (df_filtro)
        df_valor_empenhado = df_filtro[df_filtro['valor_empenhado'] < 50000]

        fig_8 = px.histogram(
            df_valor_empenhado, 
            x='valor_empenhado', 
            nbins=30, 
            labels={'valor_empenhado': 'Faixas de Valor Empenhado (R$)', 'count': 'Quantidade de Ocorrências'},
            color_discrete_sequence=["#1f77b4"]
        )

        fig_8.update_layout(
            yaxis_title="Quantidade de Empenhos",
            xaxis_title="Valor do Empenho (R$)",
            margin=dict(t=10, b=10)
        )
        st.plotly_chart(fig_8, use_container_width=True)

    with col4_graf2:
        st.markdown("**Evolução Anual do Valor Empenhado**")
        
        # Agrupamento por ano para o novo gráfico solicitado
        df_empenhado_ano = df_filtro.groupby("Ano")["valor_empenhado"].sum().reset_index()
        df_empenhado_ano = df_empenhado_ano.sort_values("Ano")
        # Forçar exibição do Ano como categoria textual para evitar decimais no eixo X (.5)
        df_empenhado_ano["Ano"] = df_empenhado_ano["Ano"].astype(str)

        fig_9 = px.bar(
            df_empenhado_ano,
            x="Ano",
            y="valor_empenhado",
            labels={"valor_empenhado": "Total Empenhado (R$)", "Ano": "Ano de Lançamento"},
            color="valor_empenhado",
            color_continuous_scale="Blues"
        )
        fig_9.update_layout(coloraxis_showscale=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_9, use_container_width=True)

    # st.divider()

    # st.markdown("**Análise de Volume vs. Gasto Financeiro (Despesa Gerencial)**")
    # df_disp = df_filtro.groupby("grupo_despesa").agg(
    #     valor_total=("valor_total", "sum"),
    #     qtd_empenhos=("n_empenho", "count")
    # ).reset_index()

    # fig_5 = px.scatter(df_disp, 
    #                     x="qtd_empenhos", 
    #                     y="valor_total", 
    #                     size="valor_total", 
    #                     color="valor_total",
    #                     text="grupo_despesa",
    #                     labels={"qtd_empenhos": "Quantidade de Empenhos Emitidos", "valor_total": "Valor Total Pago (R$)"},
    #                     size_max=40,
    #                     color_continuous_scale="Blues")

    # fig_5.update_traces(textposition="top center")

    # st.plotly_chart(fig_5, use_container_width=True)

    st.divider()

    col4_2_graf1, col4_2_graf2 = st.columns(2)

    with col4_2_graf1:
        st.markdown("**Análise por Modalidade do Empenho**")
        df_mod_emp = df_filtro.groupby("modalidade_empenho").agg(
            total=("valor_empenhado", "sum"),
            quantidade=("valor_empenhado", "count")
        ).reset_index()

        fig_mod = px.bar(
            df_mod_emp, 
            x="modalidade_empenho", 
            y="total", 
            text_auto='.2s',
            title="Valor Empenhado por Modalidade",
            labels={"total": "Total (R$)", "modalidade_empenho": "Modalidade"}
        )
        st.plotly_chart(fig_mod, use_container_width=True)

    with col4_2_graf2:
        st.markdown("**Relação Empenhado vs. Liquidado por Tipo de Despesa**")
        df_relacao = df_filtro.groupby("grupo_despesa")[["valor_empenhado", "valor_liquidado"]].sum().reset_index()

        fig_rel = px.bar(
            df_relacao, 
            x="grupo_despesa", 
            y=["valor_empenhado", "valor_liquidado"],
            barmode="group",
            title="Gargalo de Entregas por Grupo de Despesa"
        )
        st.plotly_chart(fig_rel, use_container_width=True)