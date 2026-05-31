import streamlit as st
import plotly.express as px
import utils
from scripts import previsao, graphs_config

def generate_tab(df_filtro):
    st.subheader("Métricas de Empenhos Realizados")

    total_empenhado_filtrado = df_filtro['valor_empenhado'].sum()
    qtd_empenhos_filtrado = df_filtro.shape

    # Construção do layout de cartões
    k4_1, k4_2, k4_3 = st.columns(3)
    k4_1.metric("Valor Total Empenhado (Filtro)", f"R$ {(total_empenhado_filtrado/(pow(10, 6))):,.2f} M")
    k4_2.metric("Quantidade Total de Empenhos", f"{qtd_empenhos_filtrado[0]}")
    k4_3.metric("Valor Médio por Empenho", f"R$ {(total_empenhado_filtrado/qtd_empenhos_filtrado[0]):.2f}")

    col4_graf1, col4_graf2, col4_graf3 = st.columns(3)

    with col4_graf1:
        st.subheader("**Distribuição das Faixas de Valores Empenhados**")
        # Correção do filtro para usar os dados que respeitam o painel lateral (df_filtro)
        df_valor_empenhado = df_filtro[df_filtro['valor_empenhado'] < 50000]

        fig_1 = px.histogram(
            df_valor_empenhado, 
            x='valor_empenhado', 
            nbins=30, 
            labels=utils.nomes_atributos,
            color_discrete_sequence=["#1f77b4"]
        )

        fig_1.update_layout(
            yaxis_title="Quantidade de Empenhos",
            xaxis_title="Valor do Empenho (R$)",
            margin=dict(t=10, b=10)
        )
        fig_1.update_layout(coloraxis_showscale=False, margin=dict(t=15, b=15))
        graphs_config.config_layout(fig_1)

        st.plotly_chart(fig_1, use_container_width=True)

    with col4_graf2:
        st.subheader("**Evolução Anual do Valor Empenhado**")
        
        # Agrupamento por ano para o novo gráfico solicitado
        df_empenhado_ano = df_filtro.groupby("Ano")["valor_empenhado"].sum().reset_index()
        df_empenhado_ano = df_empenhado_ano.sort_values("Ano")
        # Forçar exibição do Ano como categoria textual para evitar decimais no eixo X (.5)
        df_empenhado_ano["Ano"] = df_empenhado_ano["Ano"].astype(str)

        fig_2 = px.bar(
            df_empenhado_ano,
            x="Ano",
            y="valor_empenhado",
            labels=utils.nomes_atributos,
            color="valor_empenhado",
            color_continuous_scale="Blues"
        )
        fig_2.update_layout(coloraxis_showscale=False, margin=dict(t=15, b=15))
        graphs_config.config_layout(fig_2)

        st.plotly_chart(fig_2, use_container_width=True)

    with col4_graf3:
        st.subheader("**Análise por Modalidade do Empenho**")
        df_mod_emp = df_filtro.groupby("modalidade_empenho").agg(
            total=("valor_empenhado", "sum"),
            quantidade=("valor_empenhado", "count")
        ).reset_index()

        fig_3 = px.bar(
            df_mod_emp, 
            x="modalidade_empenho", 
            y="total", 
            text_auto='.2s',
            labels=utils.nomes_atributos
        )
        fig_3.update_layout(coloraxis_showscale=False, margin=dict(t=15, b=15))
        graphs_config.config_layout(fig_3)

        st.plotly_chart(fig_3, use_container_width=True)

    col4_2_graf1, col4_2_graf2 = st.columns([2,4])

    with col4_2_graf1:
        st.subheader("**Empenhado/Liquidado vs. Tipo de Despesa**")
        df_relacao = df_filtro.groupby("grupo_despesa")[["valor_empenhado", "valor_liquidado"]].sum().reset_index()
        df_relacao['num_grupo'] = [str(num + 1) for num in range(len(df_relacao['grupo_despesa']))]

        fig_4 = px.bar(
            df_relacao, 
            x="num_grupo", 
            y=["valor_empenhado", "valor_liquidado"],
            barmode="group",
            labels=utils.nomes_atributos,
            hover_data=['grupo_despesa']
        )

        fig_4.update_layout(coloraxis_showscale=False,
                            margin=dict(t=15, b=15),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.5))
                            # labels={'valor_empenhado': 'Valor Empenhado (R$)', 'valor_liquidado': 'Valor Liquidado (R$)'})
        graphs_config.config_layout(fig_4)

        st.plotly_chart(fig_4, use_container_width=True)

    with col4_2_graf2:
        previsao.generate_previsao(df_filtro)
