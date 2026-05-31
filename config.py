import streamlit as st

def config(page: str):
    st.set_page_config(
        page_title=page,
        page_icon="🏛️",
        layout="wide"
    )

    st.markdown("""
    <style>

    /* TIPOGRAFIA */

    h1 {
        font-size: 50px !important;
        font-weight: bold !important;
    }

    h2 {
        font-size: 40px !important;
    }

    h3 {
        font-size: 30px !important;
    }

    .stMarkdown p {
        font-size: 14px !important;
        line-height: 1.6 !important;
    }

    .stMarkdown li {
        font-size: 16px !important;
    }

    /* MÉTRICAS */

    [data-testid="stMetric"] {
        padding: 15px !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 50px !important;
        font-weight: bold !important;
        color: white !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 30px !important;
        color: #A0AEC0 !important;
    }

    /* TABS */

    [data-testid="stTabs"] button {
        padding: 23px !important;
        margin: 8px !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stTabs"] button p {
        font-size: 24px !important;
    }

    [data-testid="stTabs"] button:hover {
        color: white !important;
        background-color: #0F172A !important;
        border-radius: 10px !important;
        border: 1.5px solid #1F77B4 !important;
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.4);
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        background-color: #0F172A !important;
        border-radius: 10px !important;
        border: 1.5px solid #1F77B4 !important;
        color: white !important;
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.4);
    }

    [data-testid="stTabs"] button[aria-selected="true"] p {
        color: white !important;
    }

    /* COLUNAS */

    [data-testid="stColumn"] {
        padding: 20px !important;
        border-radius: 10px !important;
        border: 1.5px solid #1E293B !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stColumn"]:hover {
        background-color: #0F172A !important;
        border-color: #1F77B4 !important;
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(0,0,0,0.4);
    }
    </style>
    """, 
    unsafe_allow_html=True
    )