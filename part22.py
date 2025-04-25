import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Dans votre code principal, avant d'appeler part1_five et camembert5
def setup_period_filter(year):
    month_names = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    
    color_palette = {
        'primary': '#6366F1',
        'secondary': '#EC4899',
        'background': '#F3F4F6',
        # autres couleurs...
    }
    
    # Créer le slider une seule fois
    month_range = st.slider("Période", 
                         min_value=1, 
                         max_value=12, 
                         value=(1, 12),  # Valeur par défaut (début, fin)
                         step=1, 
                         help="Sélectionnez la période (mois de début et de fin)")
    
    # Stocker les valeurs dans session_state
    st.session_state.start_month, st.session_state.end_month = month_range
    
    # Afficher les mois sélectionnés
    st.caption(f"Période sélectionnée : {month_names[st.session_state.start_month-1]} à {month_names[st.session_state.end_month-1]}")
    
    # Créer la liste des mois sélectionnés et la stocker
    st.session_state.selected_months = list(range(st.session_state.start_month, st.session_state.end_month + 1))
    
    # Afficher la période sélectionnée
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-bottom: 15px; text-align: center;">
        <p style="margin: 0; font-weight: bold;">Période sélectionnée: {month_names[st.session_state.start_month-1]} à {month_names[st.session_state.end_month-1]} {year}</p>
    </div>
    """, unsafe_allow_html=True)
