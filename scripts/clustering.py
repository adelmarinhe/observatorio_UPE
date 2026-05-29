import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import plotly.express as px
import streamlit as st

import utils

numerical_cols = ['valor_empenhado', 'valor_liquidado', 'valor_total']
categorical_cols = ['unidade_gestora', 'credor', 'modalidade_empenho', 'tipo_despesa']
selected_columns = numerical_cols + categorical_cols

def create_cluster_df(df):
    df_clustering = df[selected_columns].copy()
    df_clustering[numerical_cols] = df_clustering[numerical_cols].fillna(0)
    df_clustering[categorical_cols] = df_clustering[categorical_cols].fillna('DESCONHECIDO')

    return df_clustering


def df_clustering(df):
    df_clustering = create_cluster_df(df)

    # escolha do melhor número de clusters
    scaler1 = StandardScaler()
    df_scaled = pd.DataFrame(
        scaler1.fit_transform(df_clustering[numerical_cols]),
        columns=numerical_cols
    )

    silhouette_scores_1 = []
    for k in range(2, 11):
        km = KMeans(n_clusters=k, init='k-means++', max_iter=300, n_init=10, random_state=42)
        labels = km.fit_predict(df_scaled)
        score = silhouette_score(df_scaled, labels)
        silhouette_scores_1.append(score)
        # print(f"K={k} → Silhouette Score: {score:.4f}")

    best_k1 = silhouette_scores_1.index(max(silhouette_scores_1)) + 2

    # aplicação do modelo
    kmeans_final = KMeans(n_clusters=best_k1, init='k-means++', max_iter=300, n_init=10, random_state=42)
    df_clustering['cluster'] = kmeans_final.fit_predict(df_scaled)
    
    df_clustering['cluster'] = df_clustering['cluster'].replace('0', 'Despesas Correntes')
    df_clustering['cluster'] = df_clustering['cluster'].replace('1', 'Despesas de Alto Volume')

    return df_clustering

def clustering_despesas(df):
    # df_clustering = clustering(df_filtro)

    fig_cluster = px.scatter(
        df,
        x='valor_empenhado',
        y='valor_liquidado',
        color='cluster',
        opacity=0.7,
        labels=utils.nomes_atributos,
        color_discrete_sequence=["#1f77b4", "#d62728"],
        hover_data=['credor', 'tipo_despesa', 'valor_total']
    )

    fig_cluster.update_layout(legend=dict(orientation="h", y=0.95))

    st.markdown("**Distribuição Orçamentária**")
    st.plotly_chart(fig_cluster, use_container_width=True)


def clustering_credores(df):
    # df_clustering = clustering(df_filtro)

    df_credor_cluster = df.groupby(['cluster', 'credor'])['valor_total'].sum().reset_index()

    top_5_credores = (
        df_credor_cluster.sort_values(['cluster', 'valor_total'], ascending=[True, False])
        .groupby('cluster')
        .head(5)
    )

    top_5_credores["credor_curto"] = top_5_credores["credor"].apply(lambda x: str(x)[:25] + "..." if len(str(x)) > 25 else x)

    fig_bar = px.bar(
        top_5_credores,
        x='valor_total',
        y='credor_curto',
        color='cluster',
        orientation='h',
        labels=utils.nomes_atributos,
        color_discrete_map={'Despesas Correntes': "#1f77b4", 'Despesas de Alto Volume': "#d62728"}
    )

    fig_bar.update_yaxes(categoryorder='total ascending')

    fig_bar.update_layout(coloraxis_showscale=False, 
                          xaxis_tickangle=0, 
                          yaxis={'categoryorder': 'total ascending'})

    st.markdown("**Top 5 Credores por Cluster Identificado**")
    st.plotly_chart(fig_bar, use_container_width=True)


    







    