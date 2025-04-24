import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def display_metric_card(title, value, delta=None, color="#1E88E5"):
    """Affiche une métrique dans une carte stylisée avec taille fixe"""
    # Formatage spécial pour les valeurs numériques
    if isinstance(value, (int, float)):
        # Ne pas utiliser de séparateur de milliers pour les années
        if title == "Année" or "année" in title.lower():
            formatted_value = f"{int(value)}"
        else:
            formatted_value = f"{int(value):,}".replace(",", " ")
    else:
        formatted_value = value
        
    st.markdown(
        f"""
        <div style="background-color:{color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <h3 style="color:white; margin: 0; font-size: 16px;">{title}</h3>
            <p style="color:white; font-size: 16px; font-weight: bold; margin: 5px 0;">{formatted_value}</p>
            {f'<p style="color:white; font-size: 14px; margin: 0;">Variation: {delta}</p>' if delta else ''}
        </div>
        """, 
        unsafe_allow_html=True
    )



def apply_custom_theme():
    """Applique un thème personnalisé à l'interface"""
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f5f7fa;
        }
        .main .block-container {
            padding-top: 2rem;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stDataFrame {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .stSidebar .sidebar-content {
            background-color: #f1f3f6;
        }
        .stButton button {
            background-color: #1E88E5;
            color: white;
            border-radius: 5px;
        }
        .stProgress .st-es {
            background-color: #1E88E5;
        }
        .streamlit-expanderHeader {
            background-color: #eef2f7;
            border-radius: 5px;
        }
        /* Style pour les colonnes de même hauteur */
        .equal-height-cols > div {
            min-height: 150px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def format_currency(value):
    """Formate les valeurs monétaires"""
    return f"{value:,.2f} €".replace(",", " ").replace(".", ",")

def format_number(value, is_year=False):
    """Formate les nombres avec séparateur de milliers, sauf pour les années"""
    if is_year:
        return f"{int(value)}"
    return f"{int(value):,}".replace(",", " ")
