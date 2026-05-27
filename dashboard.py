import streamlit as st
import plotly.express as px
import pandas as pd
import os

# CONFIGURAÇÃO DA PÁGINA 
st.set_page_config(page_title="UPE - Despesas Governamentais", page_icon="🏛️", layout="wide")

st.title("🏛️ UPE - Dashboard de Despesas Públicas")
st.markdown("Análise da execução orçamentária e fornecedores baseada nos dados do e-Fisco.")

# CARREGAMENTO DE DADOS 
@st.cache_data
def load_data(file):
    # Lendo o CSV delimitado por ponto e vírgula
    df = pd.read_csv(file, sep=",", encoding="utf-8")
    return df

fl = st.file_uploader("📂 Upload da planilha de Despesas (CSV)", type=["csv"])

if fl is not None:
    df = load_data(fl)
else:
    # Caso não faça upload, tenta ler um arquivo local (ajuste o caminho se necessário)
    st.info("Aguardando upload do arquivo CSV. Carregando dados de exemplo locais (se disponíveis)...")
    try:
        df = load_data("arquivos_concatenados.csv")
    except FileNotFoundError:
        st.warning("Nenhum arquivo carregado e arquivo local não encontrado.")
        st.stop()

# TRATAMENTO DE DADOS 
# Converter datas
df["Data de Lançamento"] = pd.to_datetime(df["data"], errors="coerce")
df["Ano"] = df["Data de Lançamento"].dt.year
df["Mês/Ano"] = df["Data de Lançamento"].dt.to_period("M").astype(str)

# Limpar colunas de valores (garantir que sejam float)
colunas_monetarias = ["valor_empenhado", "valor_liquidado", "valor_total"]
for col in colunas_monetarias:
    if df[col].dtype == object:
        df[col] = df[col].str.replace(',', '.', regex=False)
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# FILTROS LATERAIS (GLOBAIS) 
st.sidebar.header("🔍 Filtros Globais")

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

# ABAS DO DASHBOARD 
tab_1, tab_2, tab_3, tab_4 = st.tabs(["Gestão Executiva e Orçamentária", 
                                        "Fornecedores e Contratações", 
                                        "Alocação de Políticas Públicas",
                                        "Empenhos"])

# ABA 1: GESTÃO EXECUTIVA 
with tab_1:
    st.subheader("Visão Macro da Execução do Orçamento")
    
    total_empenhado = df_filtro["valor_empenhado"].sum()
    total_liquidado = df_filtro["valor_liquidado"].sum()
    total_pago = df_filtro["valor_total"].sum()
    indice_execucao = (total_liquidado / total_empenhado * 100) if total_empenhado > 0 else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Total Empenhado", f"R$ {total_empenhado:,.2f}")
    k2.metric("📦 Total Liquidado", f"R$ {total_liquidado:,.2f}")
    k3.metric("💸 Total Pago", f"R$ {total_pago:,.2f}")
    k4.metric("⚙️ Índice de Execução", f"{indice_execucao:.1f}%")
    
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
            labels={"value": "Valor (R$)", "variable": "Tipo de Valor", "Mês/Ano": "Mês"},
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
            labels={"valor_total": "Valor Total (R$)", "fonte_recurso": "Fonte de Recurso"},
            color="valor_total",
            color_continuous_scale="Blues"
        )
        fig2.update_layout(coloraxis_showscale=False, yaxis={'type': 'category'})
        st.plotly_chart(fig2, use_container_width=True)

# ABA 2: FORNECEDORES E CONTRATAÇÕES 
with tab_2:
    st.subheader("Análise de Mercado e Modalidades Licitatórias")
    
    credores_unicos = df_filtro["credor"].nunique()
    processos_licitatorios = df_filtro["n_licitacao"].nunique()
    
    dispensa_inex = df_filtro[
        df_filtro["modalidade_licitacao"].astype(str).str.contains("DISPENSA|INEXIGIBILIDADE", case=False, na=False)
    ]["valor_total"].sum()
    taxa_dispensa = (dispensa_inex / total_pago * 100) if total_pago > 0 else 0

    k2_1, k2_2, k2_3 = st.columns(3)
    k2_1.metric("🏢 Credores Únicos", credores_unicos)
    k2_2.metric("📄 Processos Licitatórios", processos_licitatorios)
    k2_3.metric("⚠️ Gastos por Dispensa/Inexigibilidade (%)", f"{taxa_dispensa:.1f}%")

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

    st.markdown("**Análise de Volume vs. Gasto Financeiro (Despesa Gerencial)**")
    df_disp = df_filtro.groupby("grupo_despesa").agg(
        valor_total=("valor_total", "sum"),
        qtd_empenhos=("n_empenho", "count")
    ).reset_index()

    fig_5 = px.scatter(
        df_disp, 
        x="qtd_empenhos", 
        y="valor_total", 
        size="valor_total", 
        color="valor_total",
        labels={"qtd_empenhos": "Quantidade de Empenhos Emitidos", "valor_total": "Valor Total Pago (R$)"},
        size_max=40,
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_5, use_container_width=True)
    
# ABA 3:
with tab_3:
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

# ABA 4: EMPENHOS
with tab_4:
    st.subheader("📊 Métricas de Empenhos Realizados")

    # Cálculos dos KPIs (Baseados na tabela já filtrada lateralmente)
    total_empenhado_filtrado = df_filtro['valor_empenhado'].sum()
    qtd_empenhos_filtrado = df_filtro.shape

    # Construção do layout de cartões
    k4_1, k4_2 = st.columns(2)
    k4_1.metric("💰 Valor Total Empenhado (Filtro)", f"R$ {total_empenhado_filtrado:,.2f}")
    k4_2.metric("📄 Quantidade Total de Empenhos", f"{qtd_empenhos_filtrado[0]}")

    st.divider()

    col4_graf1, col4_graf2 = st.columns(2)

    with col4_graf1:
        st.markdown("**Distribuição das Faixas de Valores Empenhados**")
        # Correção do filtro para usar os dados que respeitam o painel lateral (df_filtro)
        df_valor_empenhado = df[df['valor_empenhado'] < 50000]

        fig_8 = px.histogram(
            df_valor_empenhado, 
            x='valor_empenhado', 
            nbins=30, 
            labels={'valor_empenhado': 'Faixas de Valor Empenhado (R$)', 'count': 'Quantidade de Ocorrências'},
            color_discrete_sequence=["#1f77b4"]
        )
        # Melhorias estéticas de layout (Títulos de eixos legíveis e fundo limpo)
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

# TABELA DE DADOS & DOWNLOAD 
st.divider()
with st.expander("Tabela de Dados Brutos"):
    st.dataframe(df_filtro)

    csv = df_filtro.to_csv(index=False, sep=";").encode("utf-8")
    st.download_button(
        label="⬇️ Baixar dados filtrados (CSV)",
        data=csv,
        file_name="despesas_upe_filtradas.csv",
        mime="text/csv"
    )