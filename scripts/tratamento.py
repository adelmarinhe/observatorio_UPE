# Converter datas
import pandas as pd

def treat_dates(df):
    df["Data de Lançamento"] = pd.to_datetime(df["data"], errors="coerce")
    df["Ano"] = df["Data de Lançamento"].dt.year
    df["Mês/Ano"] = df["Data de Lançamento"].dt.to_period("M").astype(str)

    return df

# Limpar colunas de valores (garantir que sejam float)
def treat_values(df, colunas):
    for col in colunas:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df