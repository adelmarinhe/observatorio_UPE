import streamlit as st
import pandas as pd
import plotly.express as px
import utils

def generate_profile(df_filtro):
    st.subheader("Ficha Individual do Credor")
    # st.markdown("Selecione um credor específico para inspecionar seu histórico detalhado, contratos, notas e comportamento financeiro na UPE.")
    
    lista_credores_busca = sorted(df_filtro["credor"].dropna().unique())
    credor_selecionado = st.selectbox("Escolha o Fornecedor para Inspeção:", lista_credores_busca)

    if credor_selecionado:
        df_individual = df_filtro[df_filtro["credor"] == credor_selecionado].copy()
        
        # MÉTRICAS FINANCEIRAS E CONVERSÃO
        ind_emp = df_individual["valor_empenhado"].sum()
        ind_liq = df_individual["valor_liquidado"].sum()
        ind_pag = df_individual["valor_total"].sum()
        ind_notas = df_individual.shape[0]
        
        # Indicadores de eficiência operacional do contrato
        saldo_a_receber = ind_emp - ind_pag
        taxa_conversao = (ind_pag / ind_emp * 100) if ind_emp > 0 else 0
        ticket_medio = (ind_pag / ind_notas) if ind_notas > 0 else 0

        st.markdown(f"### Saúde Financeira com a Instituição")
        c_ind1, c_ind2, c_ind3, c_ind4 = st.columns(4)
        c_ind1.metric("Total Empenhado", f"R$ {ind_emp:,.2f}")
        c_ind2.metric("Total Liquidado", f"R$ {ind_liq:,.2f}")
        c_ind3.metric("Total Efetivamente Pago", f"R$ {ind_pag:,.2f}")
        c_ind4.metric("Número de Empenhos Emitidos", f"{ind_notas}")

        c_ind5, c_ind6, c_ind7, c_ind8 = st.columns(4)
        c_ind5.metric("Saldo Restante a Pagar", f"R$ {saldo_a_receber:,.2f}", delta=f"R$ {saldo_a_receber:,.2f}", delta_color="inverse")
        c_ind6.metric("Taxa de Execução (Pago/Emp)", f"{taxa_conversao:.1f}%")
        c_ind7.metric("Ticket Médio por Nota", f"R$ {ticket_medio:,.2f}")
        
        # Descobrir o ano de maior faturamento
        df_ano_max = df_individual.groupby("Ano")["valor_total"].sum()
        if not df_ano_max.empty:
            ano_pico = df_ano_max.idxmax()
            val_pico = df_ano_max.max()
            c_ind8.metric(f"Ano de Pico ({ano_pico})", f"R$ {val_pico:,.2f}")
        else:
            c_ind8.metric("Ano de Pico", "R$ 0,00")

        st.divider()

        # OBJETO DO GASTO
        # st.markdown("### Objetos de Contratação e Natureza Econômica")
        
        # col_f3, col_f4 = st.columns([2,2])
        
        # with col_f3:
            
        #     st.markdown("**Destinação por Grupo de Despesa:**")
        #     df_ind_grupo = df_individual.groupby("grupo_despesa")["valor_total"].sum().reset_index()
        #     fig_ind_grupo = px.bar(
        #         df_ind_grupo,
        #         x="valor_total", y="grupo_despesa",
        #         orientation="h",
        #         labels=utils.nomes_atributos,
        #         color="valor_total", color_continuous_scale="Purples"
        #     )
        #     fig_ind_grupo.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        #     st.plotly_chart(fig_ind_grupo, use_container_width=True)

        # with col_f4:
        #     st.markdown("**Principais Despesas Gerenciais / Classificações:**")
        #     df_ind_gerencial = df_individual.groupby("despesa")["valor_total"].sum().reset_index()
        #     df_ind_gerencial = df_ind_gerencial.sort_values(by="valor_total", ascending=False).head(5)
        #     fig_ind_ger = px.bar(
        #         df_ind_gerencial,
        #         x="valor_total", y="despesa",
        #         orientation="h",
        #         labels=utils.nomes_atributos,
        #         color="valor_total", color_continuous_scale="Greens"
        #     )
        #     fig_ind_ger.update_layout(coloraxis_showscale=False, yaxis={'categoryorder':'total ascending'})
        #     st.plotly_chart(fig_ind_ger, use_container_width=True)

        # st.divider()

        # EVOLUÇÃO TEMPORAL 
        st.markdown("### Linha do Tempo de Repasses (Mensal)")
        df_ind_tempo = df_individual.groupby("Mês/Ano")[["valor_empenhado", "valor_total"]].sum().reset_index()
        df_ind_tempo = df_ind_tempo.sort_values("Mês/Ano")

        fig_ind_line = px.line(
            df_ind_tempo,
            x="Mês/Ano",
            y=["valor_empenhado", "valor_total"],
            labels={"value": "Valor (R$)", "variable": "Fase do Gasto", "Mês/Ano": "", "valor_empenhado": "Empenhado", "valor_total": "Total"},
            color_discrete_sequence=["#ff7f0e", "#1f77b4"]
        )
        fig_ind_line.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_ind_line, use_container_width=True)

        # TABELA DE NOTAS
        st.markdown("### Histórico de Processos Licitatórios e Notas de Empenho")
        st.info("Abaixo estão listadas todas as transações, processos licitatórios vinculados e observações extraídas diretamente das notas físicas registradas para este credor.")
        
        df_ind_tabela = df_individual[[
            "n_empenho", "Ano", "unidade_gestora", "n_licitacao", "valor_empenhado", "valor_total", "obs_empenho"
        ]].copy()
        
        df_ind_tabela.columns = [
            "Empenho", "Ano", "Unidade Gestora", "N° Processo Licitatório", "Empenhado (R$)", "Pago Efetivo (R$)", "Observação"
        ]
        
        st.dataframe(df_ind_tabela.sort_values(by="Ano", ascending=False), use_container_width=True, hide_index=True)