import streamlit as st
import pandas as pd
import plotly.express as px
import utils

from scripts import graphs_config

def generate_profile(df_filtro):
    st.header("Ficha Individual do Credor")
    
    lista_credores_busca = sorted(df_filtro["credor"].dropna().unique())
    credor_selecionado = st.selectbox("Escolha o Credor:", lista_credores_busca)

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

        st.subheader(f"Saúde Financeira com a Instituição")
        c_ind1, c_ind2, c_ind3, c_ind4 = st.columns(4)
        c_ind1.metric("Total Empenhado", f"R$ {ind_emp:,.2f}")
        c_ind2.metric("Total Liquidado", f"R$ {ind_liq:,.2f}")
        c_ind3.metric("Total Efetivamente Pago", f"R$ {ind_pag:,.2f}")
        c_ind4.metric("Número de Empenhos Emitidos", f"{ind_notas}")

        c_ind5, c_ind6, c_ind7, c_ind8 = st.columns(4)
        # c_ind5.metric("Saldo Restante a Pagar", f"R$ {saldo_a_receber:,.2f}", delta=f"R$ {saldo_a_receber:,.2f}", delta_color="inverse")
        c_ind5.metric("Saldo Restante a Pagar", f"R$ {saldo_a_receber:,.2f}")
        c_ind6.metric("Taxa de Execução (Pago/Emp)", f"{taxa_conversao:.1f}%")
        c_ind7.metric("Ticket Médio por Nota", f"R$ {ticket_medio:,.2f}")
        
        df_ano_max = df_individual.groupby("Ano")["valor_total"].sum()
        if not df_ano_max.empty:
            ano_pico = df_ano_max.idxmax()
            val_pico = df_ano_max.max()
            c_ind8.metric(f"Ano de Pico ({ano_pico})", f"R$ {val_pico:,.2f}")
        else:
            c_ind8.metric("Ano de Pico", "R$ 0,00")

        # EVOLUÇÃO TEMPORAL
        col_1, col_2 = st.columns(2)

        with col_1:
             
            st.subheader("Linha do Tempo de Repasses (Mensal)")
            df_ind_tempo = df_individual.groupby("Mês/Ano")[["valor_empenhado", "valor_total", "valor_liquidado"]].sum().reset_index()
            df_ind_tempo = df_ind_tempo.sort_values("Mês/Ano")

            fig_ind_line = px.line(
                df_ind_tempo,
                x="Mês/Ano",
                y=["valor_empenhado", "valor_total", "valor_liquidado"],
                labels=utils.nomes_atributos,
                color_discrete_sequence=["#ff3c3c", "#1f77b4", "#ffffff"]
            )
            
            fig_ind_line.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            graphs_config.config_layout(fig_ind_line)
            st.plotly_chart(fig_ind_line, use_container_width=True)

        # TABELA DE NOTAS
        with col_2:
            st.subheader("Histórico de Processos Licitatórios e Notas de Empenho")
            st.info("Abaixo estão listadas todas as transações, processos licitatórios vinculados e observações extraídas diretamente das notas físicas registradas para este credor.")
            
            df_ind_tabela = df_individual[[
                "n_empenho", "Ano", "unidade_gestora", "n_licitacao", "valor_empenhado", "valor_total", "obs_empenho"
            ]].copy()
            
            df_ind_tabela.columns = [
                "Empenho", "Ano", "Unidade Gestora", "N° Processo Licitatório", "Empenhado (R$)", "Pago Efetivo (R$)", "Observação"
            ]
            
            st.dataframe(df_ind_tabela.sort_values(by="Ano", ascending=False), use_container_width=True, hide_index=True)

            csv = df_ind_tabela.to_csv(index=False, sep=";").encode("utf-8")
            st.download_button(
                label="Baixar histórico do credor (CSV)",
                data=csv,
                file_name=f"tabela_dados_credor_{credor_selecionado}.csv",
                mime="text/csv"
                )