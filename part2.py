import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime
from file1 import *
from babel.dates import format_date
import locale
locale.setlocale(locale.LC_ALL, 'C')
from datetime import datetime


def part_two(df, year, month):

    color_palette = {
        'primary': '#6366F1',         # Indigo vif
         'secondary': '#EC4899',       # Rose vif
        'tertiary': '#10B981',        # Vert émeraude
        'quaternary': '#F59E0B',      # Ambre
         'positive': '#22C55E',        # Vert succès
        'neutral': '#0EA5E9',         # Bleu ciel
        'negative': '#EF4444',        # Rouge erreur
        'background': '#F3F4F6',      # Gris très clair
     }
    
    current_month_name = format_date(datetime(2022, month, 1), 'MMMM', locale='fr')
    st.markdown(f"""
        <div style="background-color:{color_palette['primary']}; padding: 10px; border-radius: 10px;">
            <h4 style="color: white; text-align: center;">Résultats pour le mois {current_month_name} {year} </h4>
        </div>
        """, unsafe_allow_html=True)


    # Filtrer par année et mois
    filtered_df = df[(df["Year"] == year) & (df["Month"] == month)].copy()
    
    if filtered_df.empty:
        st.warning(f"Aucune donnée disponible pour {month}/{year}")
        return
        
    # Créer un identifiant unique "Matériel du fournisseur"
    filtered_df["Matériel_Fournisseur"] = filtered_df["Matériel du fournisseur"] 
        
    # Création d'un nouveau DataFrame d'analyse par commande
    # Pour chaque commande, on prendra le délai théorique max et le délai réel max des produits qui la composent
    commandes_df = filtered_df.groupby("Bon de commande").agg(
        delai_theorique=("Délai théorique", "max"),
        delai_reel=("Délai réel", "max"),
        nb_produits=("Matériel", "count"),
        fournisseur=("Fournisseur", "first"),
        nom_fournisseur=("Nom du fournisseur", "first")
    ).reset_index()

    def classer_livraison(ecart):
        if ecart < 0:
            return "En avance"
        elif 0 <= ecart <= 1:
            return "À temps"
        elif 2 <= ecart <= 7:
            return "Retard accepté"  # Ajout de "Retard accepté" pour correspondre au reste du code
        else:
            return "Long délai"
    
    # Calculer l'écart entre délai réel max et délai théorique max pour chaque commande
    commandes_df["ecart"] = commandes_df["delai_reel"] - commandes_df["delai_theorique"]
        
    commandes_df["statut_commande"] = commandes_df["ecart"].apply(classer_livraison)

    
    # ========== ANALYSE PAR PRODUIT ==========
    # Utiliser les colonnes existantes au lieu d'en créer de nouvelles
    filtered_df["theoretical_days"] = filtered_df["Délai théorique"]
    filtered_df["actual_days"] = filtered_df["Délai réel"]
    filtered_df["ecart_jours"] = filtered_df["Écart de délai"]
    filtered_df["delivery_status"] = filtered_df["Statut de livraison"]
    
    # Éviter les valeurs aberrantes (négatives ou extrêmes)
    filtered_df = filtered_df[(filtered_df["theoretical_days"] >= 0) & (filtered_df["actual_days"] >= 0)]
    
    # --- CALCUL DES MÉTRIQUES PRINCIPALES ---
    total_fournisseurs = filtered_df["Fournisseur"].nunique()
    total_materiels = filtered_df["Matériel"].nunique()
    total_commandes = filtered_df['Bon de commande'].nunique()
    
    # Calcul sur les données valides
    df_valide = filtered_df.dropna(subset=["Délai théorique", "Délai réel"])
    
    moy_delai_theorique = df_valide["Délai théorique"].mean() if not df_valide.empty else 0
    moy_delai_reel = df_valide["Délai réel"].mean() if not df_valide.empty else 0
    difference_delai = moy_delai_reel - moy_delai_theorique
    
    # --- CALCUL DES MÉTRIQUES PAR COMMANDE ---
    # Calculer le délai max pour chaque commande
    moy_delai_theorique_cmd = commandes_df["delai_theorique"].mean() if not commandes_df.empty else 0
    moy_delai_reel_cmd = commandes_df["delai_reel"].mean() if not commandes_df.empty else 0
    difference_delai_cmd = moy_delai_reel_cmd - moy_delai_theorique_cmd
    
    # KPI Produits
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>KPIS</h6>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Nombre de fournisseurs", total_fournisseurs, color="#3949AB")
    with col2:
        display_metric_card("Nombre de références", total_materiels, color="#1E88E5")
    with col3:
        display_metric_card("Nombre de commandes", total_commandes, color="#039BE5")
    
    # KPI Délais produits
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Délai des produits</h6>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        display_metric_card("Délai théorique (j)", f"{moy_delai_theorique:.1f}", color="#00897B")
    with col5:
        display_metric_card("Délai réel (j)", f"{moy_delai_reel:.1f}", color="#00ACC1")
    with col6:
        delta_color = "#4CAF50" if difference_delai <= 0 else "#F44336"
        display_metric_card("Écart moyen (j)", f"{difference_delai:.1f}", color=delta_color)
    
    # KPI Délais commandes
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Délai des commandes</h6>", unsafe_allow_html=True)
    col7, col8, col9 = st.columns(3)
    with col7:
        display_metric_card("Délai théorique (j)", f"{moy_delai_theorique_cmd:.1f}", color="#7CB342")
    with col8:
        display_metric_card("Délai réel (j)", f"{moy_delai_reel_cmd:.1f}", color="#9CCC65")
    with col9:
        delta_color = "#4CAF50" if difference_delai_cmd <= 0 else "#F44336"
        display_metric_card("Écart moyen (j)", f"{difference_delai_cmd:.1f}", color=delta_color)

    # --- VISUALISATION DES TAUX DE LIVRAISON ---
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Taux de livraison</h6>", unsafe_allow_html=True)

    # Calculs des taux (produits)
    statut_counts_produits = filtered_df["delivery_status"].value_counts(normalize=True) * 100

    # Calculs des taux (commandes)
    statut_counts_commandes = commandes_df["statut_commande"].value_counts(normalize=True) * 100
    
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
            annotations=[dict(text=f"{len(filtered_df)}\nproduits", x=0.5, y=0.5, font_size=14, showarrow=False)],
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
            annotations=[dict(text=f"{len(commandes_df)}\ncommandes", x=0.5, y=0.5, font_size=14, showarrow=False)],
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

    # ========== ANALYSE PAR PRODUIT ==========
    
    # Agréger les données par produit avec identifiant Matériel_Fournisseur
    produits_performance = filtered_df.groupby(["Matériel", "Description du matériel", "Nom du fournisseur", "Matériel_Fournisseur"]).agg(
        nb_commandes=("Bon de commande", lambda x: x.nunique()),  # nombre de commandes distinctes
        delai_theorique_moyen=("theoretical_days", "mean"),
        delai_reel_moyen=("actual_days", "mean"),
        a_temps=("delivery_status", lambda x: (x == "À temps").sum() / len(x) * 100),
        en_avance=("delivery_status", lambda x: (x == "En avance").sum() / len(x) * 100),
        retard_accepte=("delivery_status", lambda x: (x == "Retard accepté").sum() / len(x) * 100),
        long_delai=("delivery_status", lambda x: (x == "Long délai").sum() / len(x) * 100),
        livraison_plus_rapide=("actual_days", "min"),
        livraison_plus_lente=("actual_days", "max")
    ).reset_index()
    
    produits_performance["écart_moyen"] = produits_performance["delai_reel_moyen"] - produits_performance["delai_theorique_moyen"]
    
    # Arrondir les valeurs
    cols_a_arrondir = ["delai_theorique_moyen", "delai_reel_moyen", "écart_moyen", "a_temps", "en_avance", 
                       "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"]
    produits_performance[cols_a_arrondir] = produits_performance[cols_a_arrondir].round(1)
    
    # Diviser les produits en deux groupes: les meilleurs (écart <= 0) et ceux à améliorer (écart > 0)
    meilleurs_produits = produits_performance[produits_performance["écart_moyen"] <= 0].sort_values("écart_moyen", ascending=True)
    produits_a_ameliorer = produits_performance[produits_performance["écart_moyen"] > 0].sort_values("écart_moyen", ascending=False)
    
    # Section pour les meilleurs produits
    st.markdown("<h4 style='color: #000000; margin-top: 20px;'>Meilleurs produits (écart ≤ 0)</h4>", unsafe_allow_html=True)

    if meilleurs_produits.empty:
        st.info("Aucun produit avec un écart inférieur ou égal à zéro pour cette période.")
    else:
        meilleurs_produits_display = meilleurs_produits[[
            "Matériel", "Description du matériel", "Nom du fournisseur", "Matériel_Fournisseur", 
            "nb_commandes", "delai_theorique_moyen", "delai_reel_moyen", "écart_moyen",
            "en_avance", "a_temps", "retard_accepte", "long_delai", 
            "livraison_plus_rapide", "livraison_plus_lente"
        ]].rename(columns={
            "Matériel_Fournisseur": "Matériel-Fournisseur ID",
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
        
        # Reset index pour supprimer l'index, pas seulement le masquer
        meilleurs_produits_display = meilleurs_produits_display.reset_index(drop=True)
        
        # Fonction pour appliquer le style et la coloration conditionnelle
        def style_all_columns(df):
            # Créer un DataFrame vide pour les styles
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            
            # Appliquer des couleurs différentes à chaque colonne
            if "Matériel" in df.columns:
                styles["Matériel"] = 'background-color: #e3f2fd'
            if "Description du matériel" in df.columns:
                styles["Description du matériel"] = 'background-color: #f1f8e9'
            if "Nom du fournisseur" in df.columns:
                styles["Nom du fournisseur"] = 'background-color: #fff3e0'
            if "Matériel-Fournisseur ID" in df.columns:
                styles["Matériel-Fournisseur ID"] = 'background-color: #e8eaf6'
            if "Nb. commandes" in df.columns:
                styles["Nb. commandes"] = 'background-color: #e0f7fa'
            if "Délai théorique" in df.columns:
                styles["Délai théorique"] = 'background-color: #f3e5f5'
            if "Délai réel" in df.columns: 
                styles["Délai réel"] = 'background-color: #e8f5e9'
            
            # Coloration progressive pour la colonne d'écart
            if "Écart" in df.columns:
                # Fonction pour colorier l'écart en fonction de sa valeur
                def color_ecart(val):
                    if val <= -3:
                        return 'background-color: #1b5e20; color: white'  # Vert foncé (très bon)
                    elif val <= -1:
                        return 'background-color: #4caf50; color: white'  # Vert (bon)
                    elif val <= 0:
                        return 'background-color: #8bc34a'  # Vert clair (acceptable)
                    elif val <= 2:
                        return 'background-color: #ffeb3b'  # Jaune (à surveiller)
                    elif val <= 5:
                        return 'background-color: #ff9800'  # Orange (problématique)
                    else:
                        return 'background-color: #f44336; color: white'  # Rouge (critique)
                
                # Appliquer le style à la colonne Écart
                for idx in df.index:
                    val = df.loc[idx, "Écart"]
                    styles.loc[idx, "Écart"] = color_ecart(val)
            
            # Coloration des colonnes de pourcentage
            percentage_cols = ["% En avance", "% À temps", "% Retard accepté", "% Long délai"]
            for col in percentage_cols:
                if col in df.columns:
                    if col == "% En avance":
                        styles[col] = 'background-color: #bbdefb'
                    elif col == "% À temps":
                        styles[col] = 'background-color: #c8e6c9'
                    elif col == "% Retard accepté":
                        styles[col] = 'background-color: #ffecb3'
                    elif col == "% Long délai":
                        styles[col] = 'background-color: #ffccbc'
            
            # Coloration des colonnes de livraison
            if "Livraison plus rapide" in df.columns:
                styles["Livraison plus rapide"] = 'background-color: #e1f5fe'
            if "Livraison plus lente" in df.columns:
                styles["Livraison plus lente"] = 'background-color: #fce4ec'
            
            # Appliquer les styles au DataFrame
            styled_df = df.style.apply(lambda _: styles, axis=None)
            
            # Formatter les valeurs numériques
            if "Écart" in df.columns:
                styled_df = styled_df.format({
                    "Délai théorique": "{:.1f}",
                    "Délai réel": "{:.1f}",
                    "Écart": "{:.1f}",
                    "% En avance": "{:.1f}%",
                    "% À temps": "{:.1f}%",
                    "% Retard accepté": "{:.1f}%",
                    "% Long délai": "{:.1f}%",
                    "Livraison plus rapide": "{:.1f}",
                    "Livraison plus lente": "{:.1f}"
                }, na_rep="N/A")
            
            return styled_df
        
        # Afficher le tableau stylisé
        st.dataframe(style_all_columns(meilleurs_produits_display), use_container_width=True, hide_index=True)

    # Section pour les produits à améliorer
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Produits à améliorer (écart > 0)</h6>", unsafe_allow_html=True)

    if produits_a_ameliorer.empty:
        st.info("Aucun produit avec un écart supérieur à zéro pour cette période.")
    else:
        produits_a_ameliorer_display = produits_a_ameliorer[[
            "Matériel", "Description du matériel", "Nom du fournisseur", "Matériel_Fournisseur", 
            "nb_commandes", "delai_theorique_moyen", "delai_reel_moyen", "écart_moyen",
            "en_avance", "a_temps", "retard_accepte", "long_delai", 
            "livraison_plus_rapide", "livraison_plus_lente"
        ]].rename(columns={
            "Matériel_Fournisseur": "Matériel-Fournisseur ID",
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
        
        # Reset index pour supprimer l'index, pas seulement le masquer
        produits_a_ameliorer_display = produits_a_ameliorer_display.reset_index(drop=True)
        
        # Afficher le tableau stylisé
        st.dataframe(style_all_columns(produits_a_ameliorer_display), use_container_width=True, hide_index=True)

    # Agréger les données par fournisseur et par commande
    performances_fournisseurs = commandes_df.groupby(["nom_fournisseur", "fournisseur", "Bon de commande"]).agg(
        delai_theorique=("delai_theorique", "first"),
        delai_reel=("delai_reel", "first"),
        ecart=("ecart", "first"),
        statut_commande=("statut_commande", "first")
    ).reset_index()

    # Agrégation par fournisseur
    fournisseurs_performance = performances_fournisseurs.groupby(["nom_fournisseur", "fournisseur"]).agg(
        nb_commandes=("Bon de commande", "nunique"),
        delai_theorique_moyen=("delai_theorique", "mean"),
        delai_reel_moyen=("delai_reel", "mean"),
        écart_moyen=("ecart", "mean"),  # Utiliser directement l'écart existant
        a_temps=("statut_commande", lambda x: ((x == "À temps").sum() / len(x)) * 100),
        en_avance=("statut_commande", lambda x: ((x == "En avance").sum() / len(x)) * 100),
        retard_accepte=("statut_commande", lambda x: ((x == "Retard accepté").sum() / len(x)) * 100),
        long_delai=("statut_commande", lambda x: ((x == "Long délai").sum() / len(x)) * 100),
        livraison_plus_rapide=("delai_reel", "min"),
        livraison_plus_lente=("delai_reel", "max")
    ).reset_index()

    # Arrondir les valeurs
    cols_a_arrondir = ["delai_theorique_moyen", "delai_reel_moyen", "écart_moyen", "a_temps", "en_avance", 
                    "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"]
    fournisseurs_performance[cols_a_arrondir] = fournisseurs_performance[cols_a_arrondir].round(1)

    # Diviser les fournisseurs en deux groupes
    bons_fournisseurs = fournisseurs_performance[fournisseurs_performance["écart_moyen"] <= 0].sort_values("écart_moyen", ascending=True)
    fournisseurs_a_ameliorer = fournisseurs_performance[fournisseurs_performance["écart_moyen"] > 0].sort_values("écart_moyen", ascending=False)

    # Meilleurs fournisseurs
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Meilleurs fournisseurs (écart ≤ 0)</h6>", unsafe_allow_html=True)

    if bons_fournisseurs.empty:
        st.info("Aucun fournisseur avec un écart inférieur ou égal à zéro pour cette période.")
    else:
        bons_fournisseurs_display = bons_fournisseurs[[
            "nom_fournisseur", "nb_commandes", "delai_theorique_moyen",
            "delai_reel_moyen", "écart_moyen", "en_avance", "a_temps",
            "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"
        ]].rename(columns={
            "nom_fournisseur": "Nom du fournisseur",
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
        
        # Reset index
        bons_fournisseurs_display = bons_fournisseurs_display.reset_index(drop=True)
        
        # Afficher le tableau stylisé
        st.dataframe(style_all_columns(bons_fournisseurs_display), use_container_width=True, hide_index=True)

    # Fournisseurs à améliorer
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Fournisseurs à améliorer (écart > 0)</h6>", unsafe_allow_html=True)

    if fournisseurs_a_ameliorer.empty:
        st.info("Aucun fournisseur avec un écart supérieur à zéro pour cette période.")
    else:
        fournisseurs_a_ameliorer_display = fournisseurs_a_ameliorer[[
            "nom_fournisseur", "nb_commandes", "delai_theorique_moyen",
            "delai_reel_moyen", "écart_moyen", "en_avance", "a_temps",
            "retard_accepte", "long_delai", "livraison_plus_rapide", "livraison_plus_lente"
        ]].rename(columns={
            "nom_fournisseur": "Nom du fournisseur",
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
        
        # Reset index
        fournisseurs_a_ameliorer_display = fournisseurs_a_ameliorer_display.reset_index(drop=True)
        
        # Afficher le tableau stylisé
        st.dataframe(style_all_columns(fournisseurs_a_ameliorer_display), use_container_width=True, hide_index=True)


    
    
    
    # Top 10 des fournisseurs avec le plus de commandes
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Top 10 des fournisseurs avec le plus de commandes", unsafe_allow_html=True)

    
    # Compter les commandes par fournisseur
    top_vendors = filtered_df.groupby(["Fournisseur", "Nom du fournisseur"])["Bon de commande"].nunique().reset_index(name="nombre_commandes")
    top_vendors = top_vendors.sort_values("nombre_commandes", ascending=False).head(10)
    
    # Créer le graphique avec Plotly
    fig_vendors = px.bar(
        top_vendors,
        x="Nom du fournisseur",
        y="nombre_commandes",
        color="nombre_commandes",
        color_continuous_scale="Blues",
        text="nombre_commandes",
        hover_data=["Fournisseur"],
        labels={"nombre_commandes": "Nombre de commandes", "Nom du fournisseur": "Nom du fournisseur"}
    )
    
    fig_vendors.update_layout(
        title="Top 10 des fournisseurs avec le plus de commandes",
        xaxis_title="Nom du fournisseur",
        yaxis_title="Nombre de commandes",
        height=500,
        xaxis={
            'tickangle': 45,
            'type': 'category'
        }
    )
    
    fig_vendors.update_traces(
        textposition='outside',
        textfont=dict(size=12),
        marker_line_width=1.5,
        opacity=0.8
    )
    
    st.plotly_chart(fig_vendors, use_container_width=True)

    # Visualisation des matériaux les plus commandés
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Top 10 des matériaux avec le plus de commandes", unsafe_allow_html=True)

    filtered_df['Identifiant_Matériel'] = filtered_df['Matériel'] + ' / ' + filtered_df['Matériel du fournisseur']
    
    # Compter les occurrences de chaque matériel
    top_materials = filtered_df.groupby(["Identifiant_Matériel", "Description du matériel"]).size().reset_index(name="nombre_commandes")
    top_materials = top_materials.sort_values("nombre_commandes", ascending=False).head(10)
    
    # Créer l'histogramme avec Plotly
    fig_materials = px.bar(
        top_materials,
        x="Identifiant_Matériel",
        y="nombre_commandes",
        color="nombre_commandes",
        color_continuous_scale="Oranges",
        text="nombre_commandes",
        hover_data=["Description du matériel"],
        labels={"nombre_commandes": "Nombre de commandes", "Matériel": "Matériel"}
    )
    
    fig_materials.update_layout(
        title="Top 10 des matériaux les plus commandés",
        xaxis_title="Matériel",
        yaxis_title="Nombre de commandes",
        height=500,
        xaxis={
            'tickangle': 45,
            'type': 'category'
        }
    )
    
    fig_materials.update_traces(
        textposition='outside',
        textfont=dict(size=12),
        marker_line_width=1.5,
        opacity=0.8
    )
    
    st.plotly_chart(fig_materials, use_container_width=True)
    
    # Ajouter quelques informations sur les matériels
    with st.expander("Détails des matériaux les plus commandés"):
        for _, row in top_materials.iterrows():
            st.markdown(f"**{row['Identifiant_Matériel']}**:  {row['Description du matériel']} - **{row['nombre_commandes']}** commandes")
