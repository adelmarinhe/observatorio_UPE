import streamlit as st
import plotly.express as px

def generate_tab(df_filtro):
    st.subheader("Análise de Mercado e Modalidades Licitatórias")
    
    credores_unicos = df_filtro["credor"].nunique()
    processos_licitatorios = df_filtro["n_licitacao"].nunique()
    
    dispensa_inex = df_filtro[
        df_filtro["modalidade_licitacao"].astype(str).str.contains("DISPENSA|INEXIGIBILIDADE", case=False, na=False)
    ]["valor_total"].sum()

    total_pago = df_filtro["valor_total"].sum()

    taxa_dispensa = (dispensa_inex / total_pago * 100) if total_pago > 0 else 0

    k2_1, k2_2, k2_3 = st.columns(3)
    k2_1.metric("Credores Únicos", credores_unicos)
    k2_2.metric("Processos Licitatórios", processos_licitatorios)
    k2_3.metric("Gastos por Dispensa/Inexigibilidade (%)", f"{taxa_dispensa:.1f}%")

    st.divider()
    col2_1, col2_2 = st.columns(2)

    with col2_1:
        st.markdown("**Top 10 Maiores Credores (Valor Pago)**")
        df_credores = df_filtro.groupby("credor")["valor_total"].sum().reset_index()
        df_credores = df_credores.sort_values(by="valor_total", ascending=False).head(10)
        df_credores["Credor"] = df_credores["credor"].apply(lambda x: str(x)[:30] + "..." if len(str(x)) > 30 else x)

        fig_3 = px.bar(
            df_credores, 
            x="valor_total", 
            y="Credor", 
            orientation="h",
            color="valor_total",
            color_continuous_scale="Blues",
            hover_data={"credor": True}
        )
        fig_3.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_3, use_container_width=True)

    with col2_2:
        st.markdown("**Valores por Modalidade de Licitação**")
        df_modalidade = df_filtro.groupby("modalidade_licitacao")["valor_total"].sum().reset_index()
        df_modalidade = df_modalidade.sort_values("valor_total", ascending=False)
        
        fig_4 = px.bar(
            df_modalidade, 
            x="modalidade_licitacao", 
            y="valor_total",
            color="modalidade_licitacao",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_4.update_layout(showlegend=False)
        st.plotly_chart(fig_4, use_container_width=True)