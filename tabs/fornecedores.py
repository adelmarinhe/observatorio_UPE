import streamlit as st
import plotly.express as px
import utils

def generate_tab(df_filtro):
    st.subheader("Distribuição e Perfil dos Credores")
    st.markdown("Visão estratégica sobre a concentração de mercado, dependência e conformidade dos fornecedores.")

    # CÁLCULO DOS KPIS
    total_credores = df_filtro["credor"].nunique()
    total_pago_geral = df_filtro["valor_total"].sum()
    valor_medio_credor = (total_pago_geral / total_credores) if total_credores > 0 else 0
    df_saldo = df_filtro.groupby("credor").agg(
        empenhado=("valor_empenhado", "sum"),
        pago=("valor_total", "sum")
    ).reset_index()
    df_saldo["saldo_a_pagar"] = df_saldo["empenhado"] - df_saldo["pago"]
    
    if not df_saldo.empty and df_saldo["saldo_a_pagar"].max() > 0:
        maior_saldo_row = df_saldo.loc[df_saldo["saldo_a_pagar"].idxmax()]
        credor_maior_saldo = str(maior_saldo_row["credor"])[:20] + "..." if len(str(maior_saldo_row["credor"])) > 20 else maior_saldo_row["credor"]
        valor_maior_saldo = maior_saldo_row["saldo_a_pagar"]
    else:
        credor_maior_saldo = "Nenhum"
        valor_maior_saldo = 0

    # RENDERIZAÇÃO DOS CARDS
    k_cred1, k_cred2, k_cred3 = st.columns(3)
    k_cred1.metric(f"Credores Ativos", f"{total_credores:,}")
    k_cred2.metric(f"Valor Médio por Credor", f"R$ {valor_medio_credor:,.2f}")
    k_cred3.metric(f"Maior Saldo: {credor_maior_saldo}", f"R$ {valor_maior_saldo:,.2f}")

    st.divider()

    # LINHA 1 DE GRÁFICOS
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**Curva ABC de Credores**")

        df_abc = df_filtro.groupby("credor")["valor_total"].sum().reset_index()
        df_abc = df_abc.sort_values(by="valor_total", ascending=False).reset_index(drop=True)
        df_abc["pct_total"] = (df_abc["valor_total"] / total_pago_geral * 100).fillna(0)
        df_abc["pct_acumulado"] = df_abc["pct_total"].cumsum()
        
        df_abc_plot = df_abc.head(10).copy()
        df_abc_plot["credor_curto"] = df_abc_plot["credor"].apply(lambda x: str(x)[:25] + "..." if len(str(x)) > 25 else x)

        fig_abc = px.bar(
            df_abc_plot,
            x="valor_total",
            y="credor_curto",
            labels=utils.nomes_atributos,
            orientation="h",
            color="valor_total")
        
        fig_abc.update_layout(coloraxis_showscale=False, xaxis_tickangle=0, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_abc, use_container_width=True)

    with col_c2:

        st.markdown("**Evolução Histórica de Participação dos Grandes Credores**")
        df_time_cred = df_filtro.copy()

        top5_nomes = df_filtro.groupby("credor")["valor_total"].sum().nlargest(5).index
        df_time_cred["Credor_Agrupado"] = df_time_cred["credor"].apply(lambda x: x if x in top5_nomes else "OUTROS FORNECEDORES")
        
        df_time_grouped = df_time_cred.groupby(["Ano", "Credor_Agrupado"])["valor_total"].sum().reset_index()
        df_time_grouped = df_time_grouped.sort_values("Ano")
        df_time_grouped["Ano"] = df_time_grouped["Ano"].astype(str)

        fig_area = px.area(
            df_time_grouped,
            x="Ano",
            y="valor_total",
            color="Credor_Agrupado",
            labels=utils.nomes_atributos,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig_area.update_layout(barmode="stack", yaxis={'categoryorder': 'total ascending'}, legend=dict(orientation="h", y=-0.2))

        st.plotly_chart(fig_area, use_container_width=True)

    # SEÇÃO DRILLDOWN: FICHA DO CREDOR
    st.divider()
    st.subheader("Ficha Individual do Credor")
    
    lista_credores_busca = sorted(df_filtro["credor"].dropna().unique())
    credor_selecionado = st.selectbox("Escolha o Credor:", lista_credores_busca)

    if credor_selecionado:
        df_individual = df_filtro[df_filtro["credor"] == credor_selecionado]
        
        ind_emp = df_individual["valor_empenhado"].sum()
        ind_liq = df_individual["valor_liquidado"].sum()
        ind_pag = df_individual["valor_total"].sum()
        ind_notas = df_individual.shape
        
        c_ind1, c_ind2, c_ind3, c_ind4 = st.columns(4)
        c_ind1.metric("Empenhado", f"R$ {ind_emp:,.2f}")
        c_ind2.metric("Liquidado", f"R$ {ind_liq:,.2f}")
        c_ind3.metric("Pago Efetivo", f"R$ {ind_pag:,.2f}")
        c_ind4.metric("Qtd. Ocorrências (Notas)", f"{ind_notas[0]}")
        
        st.markdown(f"**Distribuição de Despesas do Credor: {credor_selecionado}**")
        df_ind_desp = df_individual.groupby("grupo_despesa")["valor_total"].sum().reset_index()
        fig_ind_bar = px.bar(
            df_ind_desp,
            x="valor_total",
            y="grupo_despesa",
            orientation="h",
            labels=utils.nomes_atributos,
            color="valor_total",
            color_continuous_scale="Mint"
        )
        fig_ind_bar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_ind_bar, use_container_width=True)