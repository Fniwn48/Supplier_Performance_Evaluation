import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
from file1 import *

def colorize_dataframe(df):
    """Applique des couleurs aux lignes du dataframe"""
    # Définir des couleurs alternées pour les lignes
    styles = [
        dict(selector="tbody tr:nth-child(even)", props=[("background-color", "#f2f2f2")]),
        dict(selector="tbody tr:nth-child(odd)", props=[("background-color", "#ffffff")]),
        dict(selector="th", props=[("background-color", "#4CAF50"), ("color", "white"), ("font-weight", "bold")]),
        dict(selector="td", props=[("text-align", "center")])
    ]
    
    # Appliquer les styles
    return df.style.set_table_styles(styles)

def part_one(df, annee):
      # Définition d'une palette de couleurs
    color_palette = {
        'primary': '#6366F1',         # Indigo vif
        'secondary': '#EC4899',       # Rose vif
        'tertiary': '#10B981',        # Vert émeraude
        'quaternary': '#F59E0B',      # Ambre
        'positive': '#22C55E',        # Vert succès
        'neutral': '#0EA5E9',         # Bleu ciel
        'negative': '#EF4444',        # Rouge erreur
        'background': '#F3F4F6',      # Gris très clair
        'text': '#1E293B'             # Bleu slate foncé
    }
    
    # Filtrer par année
    df_filtre = df[df["Year"] == annee].copy()
    
    if df_filtre.empty:
        st.warning(f"Aucune donnée disponible pour l'année {annee}")
        return
    
    # Conversion des délais en numérique
    for col in ["Délai théorique", "Délai réel"]:
        df_filtre[col] = pd.to_numeric(df_filtre[col], errors='coerce')
    

    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 10px; border-radius: 10px;">
        <h4 style="color: white; text-align: center;">Résultats pour l'année {annee}</h4>
    </div>
    """, unsafe_allow_html=True)
    

    # --- CALCUL DES MÉTRIQUES PRINCIPALES ---
    total_fournisseurs = df_filtre["Fournisseur"].nunique()
    total_materiels = df_filtre["Matériel"].nunique()
    total_commandes = df_filtre['Bon de commande'].nunique()
    
    # Calcul sur les données valides
    df_valide = df_filtre.dropna(subset=["Délai théorique", "Délai réel"])
    
    moy_delai_theorique = df_valide["Délai théorique"].mean() if not df_valide.empty else 0
    moy_delai_reel = df_valide["Délai réel"].mean() if not df_valide.empty else 0
    difference_delai = moy_delai_reel - moy_delai_theorique
    
    # --- CALCUL DES MÉTRIQUES PAR COMMANDE ---
    # Calculer le délai max pour chaque commande
    commandes_df = df_filtre.groupby('Bon de commande').agg(
        delai_theorique_max=('Délai théorique', 'max'),
        delai_reel_max=('Délai réel', 'max')
    ).reset_index()
    
    # Déterminer le statut
    commandes_df['écart'] = commandes_df['delai_reel_max'] - commandes_df['delai_theorique_max']
    
    def classer_livraison(ecart):
        if ecart < 0:
            return "En avance"
        elif 0 <= ecart <= 1:
            return "À temps"
        elif 2 <= ecart <= 7:
            return "Retard accepté" 
        else:
            return "Long délai"
        
    commandes_df["delivery_status"] = commandes_df["écart"].apply(classer_livraison)
    # Ajouter statut_commande pour correspondre au reste du code
    commandes_df["statut_commande"] = commandes_df["delivery_status"]
    
    # Calcul des statuts pour les commandes pour le graphique
    statut_counts_commandes = commandes_df["statut_commande"].value_counts(normalize=True) * 100

    # Calculs des moyennes pour les commandes
    moy_delai_theorique_cmd = commandes_df["delai_theorique_max"].mean() if not commandes_df.empty else 0
    moy_delai_reel_cmd = commandes_df["delai_reel_max"].mean() if not commandes_df.empty else 0
    difference_delai_cmd = moy_delai_reel_cmd - moy_delai_theorique_cmd
  
    
    # KPI Produits
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>KPIS", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Nombre de fournisseurs", total_fournisseurs, color="#3949AB")
    with col2:
        display_metric_card("Nombre de références", total_materiels, color="#1E88E5")
    with col3:
        display_metric_card("Nombre de commandes", total_commandes, color="#039BE5")
    
    # KPI Délais produits
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Délai des produits", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        display_metric_card("Délai théorique (j)", f"{moy_delai_theorique:.1f}", color="#00897B")
    with col5:
        display_metric_card("Délai réel (j)", f"{moy_delai_reel:.1f}", color="#00ACC1")
    with col6:
        delta_color = "#4CAF50" if difference_delai <= 0 else "#F44336"
        display_metric_card("Écart moyen (j)", f"{difference_delai:.1f}", color=delta_color)
    
    # KPI Délais commandes
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Délai des commandes", unsafe_allow_html=True)
    col7, col8, col9 = st.columns(3)
    with col7:
        display_metric_card("Délai théorique (j)", f"{moy_delai_theorique_cmd:.1f}", color="#7CB342")
    with col8:
        display_metric_card("Délai réel (j)", f"{moy_delai_reel_cmd:.1f}", color="#9CCC65")
    with col9:
        delta_color = "#4CAF50" if difference_delai_cmd <= 0 else "#F44336"
        display_metric_card("Écart moyen (j)", f"{difference_delai_cmd:.1f}", color=delta_color)

    # --- VISUALISATION DES TAUX DE LIVRAISON ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Taux de livraison", unsafe_allow_html=True)


    # Calculs des taux (produits)
    statut_counts_produits = df_filtre["Statut de livraison"].value_counts(normalize=True) * 100
    
    col1, col2 = st.columns(2)

    # Préparation de données pour les deux graphiques
    statut_labels = ["En avance", "À temps", "Retard accepté", "Long délai"]
    colors = ["#28a745", "#007bff", "#ffc107", "#dc3545"]

    with col1:
        # Graphique pour produits
        fig_taux_produits = go.Figure(go.Pie(
            labels=statut_labels,
            values=[
                statut_counts_produits.get("En avance", 0), 
                statut_counts_produits.get("À temps", 0),
                statut_counts_produits.get("Retard accepté", 0), 
                statut_counts_produits.get("Long délai", 0)
            ],
            marker=dict(colors=colors),
            hole=0.6,
            textinfo="percent",
            hoverinfo="label+percent+value",
            textfont=dict(size=12),
            insidetextorientation='radial'
        ))
        
        fig_taux_produits.update_layout(
            title="Répartition des livraisons (Produits)",
            height=350,
            annotations=[dict(text=f"{len(df_filtre)}\nproduits", x=0.5, y=0.5, font_size=14, showarrow=False)],
            legend=dict(
                orientation="v", 
                yanchor="top", 
                y=0.95, 
                xanchor="left", 
                x=1.02,
                font=dict(size=12)
            ),
            margin=dict(l=20, r=120, t=50, b=20)
        )
        
        st.plotly_chart(fig_taux_produits, use_container_width=True)

    with col2:
        # Graphique pour commandes
        fig_taux_commandes = go.Figure(go.Pie(
            labels=statut_labels,
            values=[
                statut_counts_commandes.get("En avance", 0), 
                statut_counts_commandes.get("À temps", 0),
                statut_counts_commandes.get("Retard accepté", 0), 
                statut_counts_commandes.get("Long délai", 0)
            ],
            marker=dict(colors=colors),
            hole=0.6,
            textinfo="percent",
            hoverinfo="label+percent+value",
            textfont=dict(size=12),
            insidetextorientation='radial'
        ))
        
        fig_taux_commandes.update_layout(
            title="Répartition des livraisons (Commandes)",
            height=350,
            annotations=[dict(text=f"{len(commandes_df)}\ncommandes", x=0.5, y=0.5, font_size=13, showarrow=False)],
            legend=dict(
                orientation="v", 
                yanchor="top", 
                y=0.95, 
                xanchor="left", 
                x=1.02,
                font=dict(size=12)
            ),
            margin=dict(l=20, r=120, t=50, b=20)
        )
        
        st.plotly_chart(fig_taux_commandes, use_container_width=True)

    # --- CALCUL DES PERFORMANCES DES FOURNISSEURS ---
    df_avec_commandes = pd.merge(
    df_filtre, 
    commandes_df[['Bon de commande', 'delai_theorique_max', 'delai_reel_max', 'statut_commande']], 
    on='Bon de commande', 
    how='left'
)

    # Calcul des performances par fournisseur et par commande
    performances_fournisseurs = df_avec_commandes.groupby(["Nom du fournisseur", "Fournisseur", "Bon de commande"]).agg(
        delai_theorique=("delai_theorique_max", "first"),
        delai_reel=("delai_reel_max", "first"),
        statut_commande=("statut_commande", "first")
    ).reset_index()

    # Agrégation par fournisseur
    performances_fournisseurs = performances_fournisseurs.groupby(["Nom du fournisseur", "Fournisseur"]).agg(
        nb_commandes=("Bon de commande", "nunique"),
        delai_theorique_moyen=("delai_theorique", "mean"),
        delai_reel_moyen=("delai_reel", "mean"),
        a_temps=("statut_commande", lambda x: ((x == "À temps").sum() / len(x)) * 100),
        en_avance=("statut_commande", lambda x: ((x == "En avance").sum() / len(x)) * 100),
        retard_accepte=("statut_commande", lambda x: ((x == "Retard accepté").sum() / len(x)) * 100),
        long_delai=("statut_commande", lambda x: ((x == "Long délai").sum() / len(x)) * 100),
        livraison_plus_rapide=("delai_reel", "min"),
        livraison_plus_lente=("delai_reel", "max")
    ).reset_index()

    # Calcul de l'écart moyen
    performances_fournisseurs["écart_moyen"] = performances_fournisseurs["delai_reel_moyen"] - performances_fournisseurs["delai_theorique_moyen"]

    # Séparer les fournisseurs en deux groupes
    bons_fournisseurs = performances_fournisseurs[performances_fournisseurs["écart_moyen"] <= 0].sort_values("écart_moyen")
    fournisseurs_a_ameliorer = performances_fournisseurs[performances_fournisseurs["écart_moyen"] > 0].sort_values("écart_moyen", ascending=False)

    # Fonction de style pour les tableaux de fournisseurs - inspiré par part1_one
    def style_fournisseurs_table(df):
        # Créer un DataFrame vide pour le style
        styled = pd.DataFrame('', index=df.index, columns=df.columns)
        
        # Appliquer les couleurs similaires à celles utilisées dans part1_one
        styled['Nom du fournisseur'] = 'background-color: #fff8e1'  # Couleur de 'Nom Fournisseur' dans part1_one
        styled['Nb. commandes'] = 'background-color: #e1f5fe'       # Couleur de 'Nb Commandes' dans part1_one
        styled['Délai théorique'] = 'background-color: #f5f5f5'     # Similaire à 'Nb Matériels'
        styled['Délai réel'] = 'background-color: #f5f5f5'          # Même couleur pour cohérence
        styled['% En avance'] = 'background-color: #e8f5e9'         # Couleur de 'ID Fournisseur'
        styled['% À temps'] = 'background-color: #e8f5e9'           # Même famille de couleurs
        styled['% Retard accepté'] = 'background-color: #fce4ec'    # Couleur de 'Valeur Totale'
        styled['% Long délai'] = 'background-color: #fce4ec'        # Même famille de couleurs
        styled['Livraison plus rapide'] = 'background-color: #e1f5fe'  # Même que 'Nb Commandes'
        styled['Livraison plus lente'] = 'background-color: #e1f5fe'   # Cohérence visuelle
        
        return styled

    # Colonnes à arrondir
    cols_a_arrondir = ["Délai théorique", "Délai réel", "Écart",
                    "% En avance", "% À temps", "% Retard accepté", "% Long délai",
                    "Livraison plus rapide", "Livraison plus lente"]

    # --- MEILLEURS FOURNISSEURS ---

    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Meilleurs fournisseurs (écart ≤ 0)</h4>", unsafe_allow_html=True)

    bons_fournisseurs_display = bons_fournisseurs[[
        "Nom du fournisseur", "nb_commandes", "delai_theorique_moyen",
        "delai_reel_moyen", "écart_moyen", "en_avance", "a_temps",
        "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"
    ]].rename(columns={
        "nb_commandes": "Nb. commandes",
        "delai_theorique_moyen": "Délai théorique",
        "delai_reel_moyen": "Délai réel",
        "écart_moyen": "Écart",
        "en_avance": "% En avance",
        "a_temps": "% À temps",
        "retard_accepte": "% Retard accepté",
        "long_delai": "% Long délai",
        "livraison_plus_rapide": "Livraison plus rapide",
        "livraison_plus_lente": "Livraison plus lente"
    })

    # Trier par Écart croissant
    bons_fournisseurs_display = bons_fournisseurs_display.sort_values("Écart", ascending=True)

    # Arrondir les valeurs
    bons_fournisseurs_display[cols_a_arrondir] = bons_fournisseurs_display[cols_a_arrondir].round(1)

    # Pour vraiment supprimer l'index
    bons_fournisseurs_display = bons_fournisseurs_display.reset_index(drop=True)

    # Appliquer le style avec coloration part1_one et garder le gradient sur Écart
    styled_bons_fournisseurs = bons_fournisseurs_display.style\
        .apply(style_fournisseurs_table, axis=None)\
        .background_gradient(subset=["Écart"], cmap="RdYlGn_r")\
        .format(precision=1)\
        .set_properties(**{'text-align': 'center'})\
        .hide(axis="index")

    # Afficher le tableau avec les données
    st.dataframe(styled_bons_fournisseurs, use_container_width=True, hide_index=True)


    # --- FOURNISSEURS À AMÉLIORER ---

    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Fournisseurs à améliorer (écart > 0)</h6>", unsafe_allow_html=True)

    fournisseurs_a_ameliorer_display = fournisseurs_a_ameliorer[[
        "Nom du fournisseur", "nb_commandes", "delai_theorique_moyen",
        "delai_reel_moyen", "écart_moyen", "en_avance", "a_temps", 
        "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"
    ]].rename(columns={
        "nb_commandes": "Nb. commandes",
        "delai_theorique_moyen": "Délai théorique",
        "delai_reel_moyen": "Délai réel",
        "écart_moyen": "Écart",
        "en_avance": "% En avance",
        "a_temps": "% À temps",
        "retard_accepte": "% Retard accepté",
        "long_delai": "% Long délai",
        "livraison_plus_rapide": "Livraison plus rapide",
        "livraison_plus_lente": "Livraison plus lente"
    })

    # Trier par Écart décroissant
    fournisseurs_a_ameliorer_display = fournisseurs_a_ameliorer_display.sort_values("Écart", ascending=False)

    # Arrondir les valeurs
    fournisseurs_a_ameliorer_display[cols_a_arrondir] = fournisseurs_a_ameliorer_display[cols_a_arrondir].round(1)

    # Pour vraiment supprimer l'index
    fournisseurs_a_ameliorer_display = fournisseurs_a_ameliorer_display.reset_index(drop=True)

    # Appliquer le style avec coloration part1_one et garder le gradient sur Écart
    styled_ameliorer = fournisseurs_a_ameliorer_display.style\
        .apply(style_fournisseurs_table, axis=None)\
        .background_gradient(subset=["Écart"], cmap="RdYlGn_r")\
        .format(precision=1)\
        .set_properties(**{'text-align': 'center'})\
        .hide(axis="index")

    # Afficher le tableau avec les données
    st.dataframe(styled_ameliorer, use_container_width=True, hide_index=True)

    # --- PERFORMANCE MENSUELLE ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Comparaison des délais de livraison par mois", unsafe_allow_html=True)

    
    # Ajouter une colonne de mois aux données
    if 'Month' not in df_avec_commandes.columns:
        # Assurez-vous d'avoir une colonne Date et convertissez-la en datetime si nécessaire
        if 'Date' in df_avec_commandes.columns and not pd.api.types.is_datetime64_any_dtype(df_avec_commandes['Date']):
            df_avec_commandes['Date'] = pd.to_datetime(df_avec_commandes['Date'], errors='coerce')
        
        if 'Date' in df_avec_commandes.columns:
            df_avec_commandes['Month'] = df_avec_commandes['Date'].dt.month
            df_avec_commandes['Month_Name'] = df_avec_commandes['Date'].dt.strftime('%b')
    
    # Regrouper par mois en utilisant les délais des commandes (si Month existe)
    if 'Month' in df_avec_commandes.columns:
        performance_mensuelle = df_avec_commandes.drop_duplicates('Bon de commande').groupby(["Month", "Month_Name"]).agg(
            délai_théorique_moyen=("delai_theorique_max", "mean"),
            délai_réel_moyen=("delai_reel_max", "mean"),
            nombre_commandes=("Bon de commande", "count")
        ).reset_index()
        
        # Gérer les valeurs NaN et trier
        performance_mensuelle = performance_mensuelle.fillna(0).sort_values("Month")
        
        # Calculer l'écart
        performance_mensuelle["écart"] = performance_mensuelle["délai_réel_moyen"] - performance_mensuelle["délai_théorique_moyen"]
        
        # Créer le graphique avec Plotly
        fig_mensuelle = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Ajouter les lignes pour délai théorique et réel
        fig_mensuelle.add_trace(
            go.Scatter(
                x=performance_mensuelle["Month_Name"], 
                y=performance_mensuelle["délai_théorique_moyen"].round(1),
                mode='lines+markers+text',
                name='Délai théorique',
                line=dict(color='#007bff', width=3),
                marker=dict(size=8),
                text=performance_mensuelle["délai_théorique_moyen"].round(1),
                textposition="top center"
            ),
            secondary_y=False
        )
        
        fig_mensuelle.add_trace(
            go.Scatter(
                x=performance_mensuelle["Month_Name"], 
                y=performance_mensuelle["délai_réel_moyen"].round(1),
                mode='lines+markers+text',
                name='Délai réel',
                line=dict(color='#dc3545', width=3),
                marker=dict(size=8),
                text=performance_mensuelle["délai_réel_moyen"].round(1),
                textposition="top center"
            ),
            secondary_y=False
        )
        
        # Ajouter les barres pour l'écart
        fig_mensuelle.add_trace(
            go.Bar(
                x=performance_mensuelle["Month_Name"],
                y=performance_mensuelle["écart"].round(1),
                name='Écart',
                marker_color=['#28a745' if x <= 0 else '#dc3545' for x in performance_mensuelle["écart"]],
                opacity=0.5,
                text=performance_mensuelle["écart"].round(1),
                textposition="auto"
            ),
            secondary_y=True
        )
        
        # Mise à jour de la mise en page
        fig_mensuelle.update_layout(
            title="Performance de livraison par mois (basée sur les commandes)",
            xaxis_title="Mois",
            yaxis_title="Jours de délai",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=500,
            hovermode="x"
        )
        
        fig_mensuelle.update_yaxes(title_text="Jours de délai", secondary_y=False)
        fig_mensuelle.update_yaxes(title_text="Écart de délai (jours)", secondary_y=True)
        
        st.plotly_chart(fig_mensuelle, use_container_width=True)
    else:
        st.warning("Données de mois non disponibles pour l'analyse mensuelle")
    
    # --- TOP 10 DES PRODUITS LES PLUS COMMANDÉS ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Top 10 des produits les plus commandés", unsafe_allow_html=True)

    # Compter les occurrences de chaque matériel
    top_materiels = df_filtre.groupby(["Matériel", "Description du matériel"]).size().reset_index(name="nombre_materiaux")
    top_materiels = top_materiels.sort_values("nombre_materiaux", ascending=False).head(10)
    
    # Créer l'histogramme avec Plotly
    fig_materiels = px.bar(
        top_materiels,
        x="Matériel",
        y="nombre_materiaux",
        color="nombre_materiaux",
        color_continuous_scale="Oranges",
        text="nombre_materiaux",
        hover_data=["Description du matériel"],
        labels={"nombre_materiaux": "Nombre de matériel", "Matériel": "Matériel"}
    )
    
    fig_materiels.update_layout(
        title="Top 10 des produits les plus commandés",
        xaxis_title="Matériel",
        yaxis_title="Nombre de matériel",
        height=500,
        xaxis={
            'tickangle': 45,
            'type': 'category'
        }
    )
    
    fig_materiels.update_traces(
        textposition='outside',
        textfont=dict(size=12),
        marker_line_width=1.5,
        opacity=0.8
    )
    
    st.plotly_chart(fig_materiels, use_container_width=True)
    
    # --- ANALYSE DÉTAILLÉE DES PRODUITS ---
    # Regrouper par matériel et calculer toutes les métriques
    produits_analyse = df_filtre.groupby(["Matériel", "Description du matériel"]).agg(
        nombre_commandes=("Bon de commande", "nunique"),
        délai_théorique_moyen=("Délai théorique", "mean"),
        délai_réel_moyen=("Délai réel", "mean"),
        en_avance=("Statut de livraison", lambda x: ((x == "En avance").sum() / len(x)) * 100),
        a_temps=("Statut de livraison", lambda x: ((x == "À temps").sum() / len(x)) * 100),
        retard_accepte=("Statut de livraison", lambda x: ((x == "Retard accepté").sum() / len(x)) * 100),
        long_delai=("Statut de livraison", lambda x: ((x == "Long délai").sum() / len(x)) * 100),
        fournisseurs=("Nom du fournisseur", lambda x: ', '.join([str(f) for f in pd.unique(x)]))
    ).reset_index()

    # Calculer l'écart
    produits_analyse["écart"] = produits_analyse["délai_réel_moyen"] - produits_analyse["délai_théorique_moyen"]

    # Arrondir les valeurs numériques
    for col in ["délai_théorique_moyen", "délai_réel_moyen", "écart", "en_avance", "a_temps", "retard_accepte", "long_delai"]:
        produits_analyse[col] = produits_analyse[col].round(1)

    # Séparation des produits en deux catégories selon l'écart
    produits_bons = produits_analyse[produits_analyse["écart"] <= 0].sort_values("écart")
    produits_a_ameliorer = produits_analyse[produits_analyse["écart"] > 0].sort_values("écart", ascending=False)

    # Fonction de style pour les tableaux de produits - similaire à celle des fournisseurs
    def style_produits_table(df):
        # Créer un DataFrame vide pour le style
        styled = pd.DataFrame('', index=df.index, columns=df.columns)
        
        # Appliquer les couleurs similaires à celles utilisées pour les fournisseurs
        styled['Matériel'] = 'background-color: #fff8e1'
        styled['Description du matériel'] = 'background-color: #fff8e1'
        styled['Nb. commandes'] = 'background-color: #e1f5fe'
        styled['Délai théorique'] = 'background-color: #f5f5f5'
        styled['Délai réel'] = 'background-color: #f5f5f5'
        styled['% En avance'] = 'background-color: #e8f5e9'
        styled['% À temps'] = 'background-color: #e8f5e9'
        styled['% Retard accepté'] = 'background-color: #fce4ec'
        styled['% Long délai'] = 'background-color: #fce4ec'
        styled['Fournisseurs'] = 'background-color: #e1f5fe'
        
        return styled

    # --- MEILLEURS PRODUITS ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Meilleurs produits (écart ≤ 0)</h6>", unsafe_allow_html=True)

    bons_produits_display = produits_bons[[
        "Matériel", "Description du matériel", "nombre_commandes", "délai_théorique_moyen",
        "délai_réel_moyen", "écart", "en_avance", "a_temps",
        "retard_accepte", "long_delai", "fournisseurs"
    ]].rename(columns={
        "nombre_commandes": "Nb. commandes",
        "délai_théorique_moyen": "Délai théorique",
        "délai_réel_moyen": "Délai réel",
        "écart": "Écart",
        "en_avance": "% En avance",
        "a_temps": "% À temps",
        "retard_accepte": "% Retard accepté",
        "long_delai": "% Long délai",
        "fournisseurs": "Fournisseurs"
    })

    # Trier par Écart croissant
    bons_produits_display = bons_produits_display.sort_values("Écart", ascending=True)

    # Pour vraiment supprimer l'index
    bons_produits_display = bons_produits_display.reset_index(drop=True)

    # Appliquer le style avec coloration et gradient sur Écart
    styled_bons_produits = bons_produits_display.style\
        .apply(style_produits_table, axis=None)\
        .background_gradient(subset=["Écart"], cmap="RdYlGn_r")\
        .format(precision=1)\
        .set_properties(**{'text-align': 'center'})\
        .hide(axis="index")

    # Afficher le tableau avec les données
    st.dataframe(styled_bons_produits, use_container_width=True, hide_index=True)

    # --- PRODUITS À AMÉLIORER ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Produits à améliorer (écart > 0)</h6>", unsafe_allow_html=True)

    produits_a_ameliorer_display = produits_a_ameliorer[[
        "Matériel", "Description du matériel", "nombre_commandes", "délai_théorique_moyen",
        "délai_réel_moyen", "écart", "en_avance", "a_temps", 
        "retard_accepte", "long_delai", "fournisseurs"
    ]].rename(columns={
        "nombre_commandes": "Nb. commandes",
        "délai_théorique_moyen": "Délai théorique",
        "délai_réel_moyen": "Délai réel",
        "écart": "Écart",
        "en_avance": "% En avance",
        "a_temps": "% À temps",
        "retard_accepte": "% Retard accepté",
        "long_delai": "% Long délai",
        "fournisseurs": "Fournisseurs"
    })

    # Trier par Écart décroissant
    produits_a_ameliorer_display = produits_a_ameliorer_display.sort_values("Écart", ascending=False)

    # Pour vraiment supprimer l'index
    produits_a_ameliorer_display = produits_a_ameliorer_display.reset_index(drop=True)

    # Appliquer le style avec coloration et gradient sur Écart
    styled_produits_ameliorer = produits_a_ameliorer_display.style\
        .apply(style_produits_table, axis=None)\
        .background_gradient(subset=["Écart"], cmap="RdYlGn_r")\
        .format(precision=1)\
        .set_properties(**{'text-align': 'center'})\
        .hide(axis="index")

    # Afficher le tableau avec les données
    st.dataframe(styled_produits_ameliorer, use_container_width=True, hide_index=True)
