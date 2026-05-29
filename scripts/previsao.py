import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import utils
import streamlit as st

try:
    from xgboost import XGBRegressor
    XGBOOST_OK = True
except ImportError:
    XGBOOST_OK = False
    print("XGBoost não instalado. Será ignorado.")

print("Bibliotecas carregadas com sucesso!")

def prever_n_meses(ts_base, model, scaler_obj, target_var, features, n_meses=3, usar_scaler=False):
    """Previsão recursiva: cada predição alimenta os lags seguintes."""
    # Garante que estamos trabalhando com uma estrutura limpa contendo apenas o histórico real consolidado
    ts_ext = ts_base[['data', target_var]].copy()
    ts_ext['data'] = pd.to_datetime(ts_ext['data'])
    
    futuras = []

    for _ in range(n_meses):
        # 1. Obter a próxima data cronológica
        prox_data = ts_ext['data'].iloc[-1] + pd.DateOffset(months=1)
        
        # 2. Criar dicionário base para a nova linha de features
        nova_linha_feat = {
            'ano': prox_data.year,
            'mes': prox_data.month,
            'trimestre': prox_data.quarter
        }
        
        # 3. Recalcular Lags usando o histórico disponível em ts_ext
        for lag in [1, 2, 3, 6, 12]:
            val = ts_ext[target_var].iloc[-lag] if len(ts_ext) >= lag else np.nan
            nova_linha_feat[f'lag_{lag}'] = val

        # 4. Recalcular Estatísticas Móveis (Média, Desvio Padrão e Variação)
        nova_linha_feat['mm_3'] = ts_ext[target_var].iloc[-3:].mean() if len(ts_ext) >= 3 else np.nan
        nova_linha_feat['mm_6'] = ts_ext[target_var].iloc[-6:].mean() if len(ts_ext) >= 6 else np.nan
        nova_linha_feat['mm_12'] = ts_ext[target_var].iloc[-12:].mean() if len(ts_ext) >= 12 else np.nan
        nova_linha_feat['std_3'] = ts_ext[target_var].iloc[-3:].std() if len(ts_ext) >= 3 else 0.0
        
        # Variação percentual do último mês
        if len(ts_ext) >= 2:
            v_atual = ts_ext[target_var].iloc[-1]
            v_anterior = ts_ext[target_var].iloc[-2]
            nova_linha_feat['var_pct_1'] = (v_atual - v_anterior) / v_anterior if v_anterior != 0 else 0.0
        else:
            nova_linha_feat['var_pct_1'] = 0.0

        # Convertendo em DataFrame ordenado pelas features esperadas pelo modelo
        df_row = pd.DataFrame([nova_linha_feat])[features]
        row_values = df_row.values.reshape(1, -1)
        
        if usar_scaler:
            row_values = scaler_obj.transform(row_values)

        # 5. Predição do modelo
        pred = float(model.predict(row_values)[0])
        
        # Evita previsões de valores negativos para orçamento/empenho se não fizer sentido
        if pred < 0: 
            pred = 0.0

        # 6. Atualiza a base para o próximo passo do loop recursivo
        nova_linha_historico = pd.DataFrame({'data': [prox_data], target_var: [pred]})
        ts_ext = pd.concat([ts_ext, nova_linha_historico], ignore_index=True)
        
        futuras.append({'data': prox_data, 'desembolso_previsto': pred})

    return pd.DataFrame(futuras)

def generate_previsao(df_filtro):
    # Tratamento inicial dos dados filtrados
    df_evolucao = df_filtro[['data', 'valor_empenhado']].copy()
    df_evolucao["data"] = pd.to_datetime(df_evolucao["data"], errors="coerce")
    
    # Agrupamento mensal convertendo o período de volta para o primeiro dia do mês (Timestamp)
    df_evolucao["mes_ano"] = df_evolucao["data"].dt.to_period("M")
    df_mensal = df_evolucao.groupby("mes_ano")['valor_empenhado'].sum().reset_index()
    df_mensal = df_mensal.sort_values("mes_ano")
    df_mensal['data'] = df_mensal['mes_ano'].dt.to_timestamp()

    ts_feat = df_mensal.copy()

    # Engenharia de Features Temporais
    ts_feat['ano'] = ts_feat['data'].dt.year
    ts_feat['mes'] = ts_feat['data'].dt.month
    ts_feat['trimestre'] = ts_feat['data'].dt.quarter

    # Lags (valores passados)
    for lag in [1, 2, 3, 6, 12]:
        ts_feat[f'lag_{lag}'] = ts_feat['valor_empenhado'].shift(lag)

    # Médias móveis baseadas no passado imediato (shift 1 evita vazamento de dados do target)
    ts_feat['mm_3']  = ts_feat['valor_empenhado'].shift(1).rolling(3).mean()
    ts_feat['mm_6']  = ts_feat['valor_empenhado'].shift(1).rolling(6).mean()
    ts_feat['mm_12'] = ts_feat['valor_empenhado'].shift(1).rolling(12).mean()

    # Desvio padrão móvel (volatilidade)
    ts_feat['std_3'] = ts_feat['valor_empenhado'].shift(1).rolling(3).std()

    # Variação percentual mês a mês
    ts_feat['var_pct_1'] = ts_feat['valor_empenhado'].shift(1).pct_change(1)

    # Remove NaNs gerados pelos históricos iniciais incompletos
    ts_model = ts_feat.dropna().reset_index(drop=True)

    features = ['ano', 'mes', 'trimestre', 'lag_1', 'lag_2', 'lag_3', 'lag_6', 'lag_12', 'mm_3', 'mm_6', 'mm_12', 'std_3', 'var_pct_1']
    target = 'valor_empenhado'

    x = ts_model[features]
    y = ts_model[target]

    split_idx = int(len(ts_model) * 0.8)

    X_train, X_test = x.iloc[:split_idx], x.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    best_model = XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42, verbosity=0)
    
    usar_sc = False 
    best_model.fit(X_train, y_train)

    # Execução das previsões futuras de forma recursiva
    previsoes = prever_n_meses(
        ts_base=ts_model[['data', 'valor_empenhado']],
        model=best_model, 
        scaler_obj=scaler, 
        target_var='valor_empenhado', 
        features=features,
        n_meses=3, 
        usar_scaler=usar_sc
    )

    previsoes['desembolso_previsto_fmt'] = previsoes['desembolso_previsto'].apply(lambda val: f'R$ {val:,.2f}')
    
    # Configuração do Plotly: Histórico + Próximos 3 Meses
    n_hist = 24
    historico = ts_model[['data', 'valor_empenhado']].tail(n_hist).copy()
    historico['Status'] = 'Histórico'

    df_prev_plot = previsoes[['data', 'desembolso_previsto']].copy()
    df_prev_plot.columns = ['data', 'valor_empenhado']
    df_prev_plot['Status'] = 'Previsão (3 meses)'

    ponte = pd.DataFrame({
        'data': [historico['data'].iloc[-1], df_prev_plot['data'].iloc[0]],
        'valor_empenhado': [historico['valor_empenhado'].iloc[-1], df_prev_plot['valor_empenhado'].iloc[0]],
        'Status': ['Transição', 'Transição']
    })

    df_final_plot = pd.concat([historico, ponte, df_prev_plot], ignore_index=True)
    st.markdown("**Previsão de Execução Orçamentária para os Próximos 3 Meses (XGBoost)**")
    fig_previsao = px.line(
        df_final_plot, 
        x='data', 
        y='valor_empenhado', 
        color='Status',
        markers=True,
        color_discrete_map={
            'Histórico': '#1a6db5',
            'Previsão (3 meses)': "#ffffff",
            'Transição': "#ffffff"
        }
    )

    fig_previsao.for_each_trace(lambda t: t.update(line=dict(dash='dot')) if t.name == 'Transição' else ())
    fig_previsao.for_each_trace(lambda t: t.update(line=dict(dash='dash'), marker=dict(symbol='star', size=10)) if t.name == 'Previsão (3 meses)' else ())
    
    fig_previsao.for_each_trace(lambda t: t.update(showlegend=False) if t.name == 'Transição' else ())

    fig_previsao.update_layout(
        xaxis_title='Mês', 
        yaxis_title='Desembolso (R$)',
        hovermode='x unified',
        yaxis_tickformat=',.0f', 
        height=480
    )

    st.plotly_chart(fig_previsao, use_container_width=True)


