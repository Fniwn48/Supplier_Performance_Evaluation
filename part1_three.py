import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

from file1 import *



def part1_three(df, year, month, vendor_search):
    """
    Affiche les résultats des commandes pour une année, un mois et un fournisseur spécifiques.
    
    Parameters:
    -----------
    df : DataFrame
        Le DataFrame contenant les données de commandes
    year : int ou str
        L'année sélectionnée pour l'analyse
    month : int ou str
        Le mois sélectionné pour l'analyse
    vendor_search : str
        L'identifiant ou le nom du fournisseur recherché
    """
   
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
    

    df = df[(df['Nom du fournisseur'] == vendor_search) | 
                     (df['Fournisseur'] == vendor_search)].copy()
    
    if df.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {vendor_search}")
        return
   

   # Ensuite filtrer par année et mois 
    df = df[(df['Year'] == year) & (df['Month'] == month)]

    # Vérifier si le dataframe est vide après le second filtre
    if df.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {vendor_search} en mois {month} {year}")
        return

    current_month_name = datetime(2022, month, 1).strftime('%B')
    # Titre et description de la section
    st.markdown(f"""
    <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h4 style="color: white;text-align: center; margin: 0;">Analyse des Commandes pour {vendor_search} pour le mois {current_month_name} {year}</h4>
    </div>
    """, unsafe_allow_html=True)

    # Afficher les indicateurs clés (KPIs) pour le fournisseur sélectionné
    total_orders = df["Bons de commande"].nunique()
    total_materials = df["Matériel"].nunique()
    total_value = df["Valeur nette de la commande"].sum()
    
    # Affichage des KPIs dans 4 colonnes avec les mêmes couleurs que dans part1_two
    st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Bons de commande", total_orders, color="#3498db")
    with col2:
        display_metric_card("Matériels uniques", total_materials, color="#2ecc71")
    with col3:
        display_metric_card("Valeur totale", format_currency(total_value), color="#f39c12")
   
    
    # Analyse détaillée des produits pour ce fournisseur
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Détail des Matériels Commandés</h6>", unsafe_allow_html=True)

    
    
    # Regrouper les données par matériel
    material_summary = df.groupby(["Matériel", "Description du matériel", "Matériel du fournisseur"]).agg(
        nb_commandes=("Bons de commande", "nunique"),
        nb_lignes=("Bons de commande", "count"),
        unite_achat=("Order Unit", "first"), 
        qte_somme=("Order Quantity", "sum"),
        qte_min=("Order Quantity", "min"),
        qte_max=("Order Quantity", "max"),
        qte_moy=("Order Quantity", "mean"),
        valeur_totale=("Valeur nette de la commande", "sum"),
    ).reset_index()

    # Trier par valeur totale (décroissant)
    material_summary = material_summary.sort_values(by="valeur_totale", ascending=False)

    # Renommer les colonnes pour l'affichage
    material_summary = material_summary.rename(columns={
        "Matériel": "Matériel",
        "Description du matériel": "Description",
        "Matériel du fournisseur": "Réf. Fournisseur",
        "nb_commandes": "Nb Commandes",
        "nb_lignes": "Nb Lignes",
        "unite_achat":"Order Unit",
        "qte_somme": "Qté Totale",
        "qte_min": "Qté Min",
        "qte_max": "Qté Max",
        "qte_moy": "Qté Moyenne",
        "valeur_totale": "Valeur Totale",
    })

    # Formater les colonnes numériques
    material_summary["Valeur Totale"] = material_summary["Valeur Totale"].apply(format_currency)
    # Formater les colonnes de quantité
    material_summary["Qté Moyenne"] = material_summary["Qté Moyenne"].apply(lambda x: f"{x:.1f}")  # Un chiffre après la virgule
    material_summary["Qté Totale"] = material_summary["Qté Totale"].apply(lambda x: f"{int(x)}")  # Pas de décimales
    material_summary["Qté Min"] = material_summary["Qté Min"].apply(lambda x: f"{int(x)}")  # Pas de décimales
    material_summary["Qté Max"] = material_summary["Qté Max"].apply(lambda x: f"{int(x)}")  # Pas de décimales

    # Créer un style pour l'ensemble du DataFrame des matériels avec des couleurs par colonnes
    def highlight_columns_material(x):
        df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
        df_styler['Matériel'] = 'background-color: #e3f2fd'
        df_styler['Description'] = 'background-color: #f1f8e9'  
        df_styler['Réf. Fournisseur'] = 'background-color: #e8eaf6'
        df_styler['Nb Commandes'] = 'background-color: #e0f7fa'
        df_styler['Nb Lignes'] = 'background-color: #f3e5f5'
        df_styler['Order Unit'] = 'background-color: #f5f5f5'
        df_styler['Qté Min'] = 'background-color: #fce4ec'
        df_styler['Qté Max'] = 'background-color: #f3e5f5'
        df_styler['Qté Moyenne'] = 'background-color: #e8f5e9'
        df_styler['Qté Totale'] = 'background-color: #fff8e1'
        df_styler['Valeur Totale'] = 'background-color: #ffebee'
        return df_styler

    # Appliquer le style avec coloration des colonnes
    styled_material_df = material_summary.style.apply(highlight_columns_material, axis=None)

    # Afficher le tableau avec les données et les couleurs
    st.dataframe(styled_material_df, use_container_width=True, hide_index=True)
    
    # Top 10 des produits les plus commandés en valeur
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Top 10 des Produits les Plus Commandés</h6>", unsafe_allow_html=True)

    # Pour les graphiques, utilisez les données avant formatage
    top_products = df.groupby(["Matériel", "Matériel du fournisseur","Description du matériel"]).agg(
        nb_lignes=("Bons de commande", "count"),
        nb_commandes=("Bons de commande", "nunique"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()

    # Trier par valeur totale et prendre les 10 premiers
    top_products = top_products.sort_values(by="valeur_totale", ascending=False).head(10)

    # Créer le graphique pour les produits les plus commandés (en valeur)
    fig_top_products = go.Figure()

    # Ajouter les barres pour la valeur totale (axe Y gauche)
    fig_top_products.add_trace(go.Bar(
        x=top_products["Matériel"],
        y=top_products["valeur_totale"],
        name='Valeur Totale (€)',
        marker=dict(color='#FF7F00'),
        opacity=0.85,
        hovertemplate='<b>%{x}</b><br>Valeur: %{y:,.2f} €<extra></extra>'
    ))

    # Ajouter une ligne pour le nombre de lignes (axe Y droit)
    fig_top_products.add_trace(go.Scatter(
        x=top_products["Matériel"],
        y=top_products["nb_lignes"],
        mode='lines+markers',
        name='Nb Lignes',
        line=dict(color='#6A0DAD', width=3),
        marker=dict(size=9, symbol='diamond'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Nb Lignes: %{y:,.0f}<extra></extra>'
    ))

    # Configuration des axes et du layout
    fig_top_products.update_layout(
        title={
            'text': f"Top 10 des produits pour le mois {month}-{year}",
            'font': {'size': 13, 'color': '#505050'},
            'y': 0.95
        },
        xaxis=dict(
            title='Produit',
            tickangle=-45
        ),
        yaxis=dict(
            title_text='Valeur Totale (€)',
            title_font=dict(color='#FF7F00'),
            tickfont=dict(color='#FF7F00')
        ),
        yaxis2=dict(
            title_text='Nb Lignes',
            title_font=dict(color='#6A0DAD'),
            tickfont=dict(color='#6A0DAD'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        height=550,
        template='plotly_white'
    )

    # Afficher le graphique
    st.plotly_chart(fig_top_products, use_container_width=True)

    
    # Ajouter un expander avec le tableau récapitulatif des produits (top 10)
    with st.expander("📊 Détails des produits les plus commandés", expanded=False):
        # Préparation du tableau récapitulatif
        products_summary_top = top_products.rename(columns={
            "Matériel": "Produit", 
            "Matériel du fournisseur": "Réf. Fournisseur",
            "Description du matériel": "Description", 
            "nb_lignes": "Nb Lignes", 
            "nb_commandes": "Nb Commandes",
            "valeur_totale": "Valeur Totale"
        })
        
        # Formater la valeur totale
        products_summary_top["Valeur Totale"] = products_summary_top["Valeur Totale"].apply(
            lambda x: f"{x:,.2f} €".replace(",", " ").replace(".", ",")
        )
        
        for _, row in products_summary_top.iterrows():
            # Créer une ligne descriptive avec les valeurs colorées, en commençant par le code matériel
            st.markdown(
                f"<b>Matériel {row['Produit']}-{row['Réf. Fournisseur']}</b> - {row['Description']} : "
                f"<span style='color:#FF7F00; font-weight:bold;'>{row['Valeur Totale']}</span>, "
                f"<span style='color:#6A0DAD; font-weight:bold;'>{int(row['Nb Lignes'])}</span> lignes, "
                f"<span style='color:#DB4437; font-weight:bold;'>{int(row['Nb Commandes'])}</span> commandes",
                unsafe_allow_html=True
            )



def camembert3(df,year,month,vendor_search):

    df = df[(df['Nom du fournisseur'] == vendor_search) | 
                     (df['Fournisseur'] == vendor_search)].copy()
    
    if df.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {vendor_search}")
        return
   

   # Ensuite filtrer par année et mois 
    df = df[(df['Year'] == year) & (df['Month'] == month)]

    # Vérifier si le dataframe est vide après le second filtre
    if df.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {vendor_search} en mois {month} {year}")
        return
    # Répartition par Gamme de Produits
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Répartition par Gamme de Produits</h6>", unsafe_allow_html=True)

    # Regrouper les données par prodline
    prodline_summary = df.groupby("Prodline Name").agg(
        nb_commandes=("Bons de commande", "nunique"),
        qte_totale=("Order Quantity", "sum"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()

    # Trier par valeur totale
    prodline_summary = prodline_summary.sort_values(by="valeur_totale", ascending=False)

    # Créer les labels personnalisés pour le camembert
    prodline_summary['labels'] = prodline_summary.apply(
        lambda row: f"{row['Prodline Name']}: {format_currency(row['valeur_totale'])}<br>"
                f"({int(row['qte_totale'])} unités, {int(row['nb_commandes'])} commandes)", 
        axis=1
    )

    # Palette de couleurs sophistiquées (réutilisation de celle définie plus haut ou utilisation de cette palette spécifique)
    color_palette_pie = [
        '#5D4E7B', '#8A7AAF', '#A799CE', '#C4BAE0', '#D3C4E3',
        '#26495C', '#4C86A8', '#68B0AB', '#8FC0A9', '#C8D5B9',
        '#AC3B61', '#D63B77', '#EF5D92', '#F283B6', '#FBAFC4'
    ]

    # Créer le camembert
    fig_pie = go.Figure(data=[go.Pie(
        labels=prodline_summary['Prodline Name'],
        values=prodline_summary['valeur_totale'],
        text=prodline_summary['labels'],
        hoverinfo='text',
        textinfo='percent',
        hole=0.4,
        marker=dict(colors=color_palette_pie, line=dict(color='#FFFFFF', width=1.5)),
        textfont=dict(size=14),
        rotation=45
    )])

    # Mise en forme du graphique
    current_month_name = datetime(2022, month, 1).strftime('%B')
    fig_pie.update_layout(
        title={
            'text': f"Répartition des produits par gamme pour le mois de {current_month_name} {year}",
            'font': {'size': 13, 'color': '#505050'},
            'y': 0.95
        },
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.4,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        height=500,
        template='plotly_white',
        margin=dict(t=80, b=80, l=40, r=40)
    )

    # Ajouter des annotations au centre du camembert
    fig_pie.add_annotation(
        text=f"<b>Total<br>{format_currency(prodline_summary['valeur_totale'].sum())}</b>",
        x=0.5, y=0.5,
        font=dict(size=16, color='#505050'),
        showarrow=False
    )

    # Afficher le graphique
    st.plotly_chart(fig_pie, use_container_width=True)

    # Ajouter un expander avec le tableau récapitulatif
    with st.expander("📊 Détail par gamme de produits", expanded=False):
        # Préparation du tableau récapitulatif
        prodline_table = prodline_summary[['Prodline Name', 'nb_commandes', 'qte_totale', 'valeur_totale']].copy()
        
        # Renommer les colonnes
        prodline_table = prodline_table.rename(columns={
            "Prodline Name": "Gamme de Produits", 
            "nb_commandes": "Commandes", 
            "qte_totale": "Quantité", 
            "valeur_totale": "Valeur Totale"
        })
        
        # Formater les colonnes
        prodline_table["Valeur Totale"] = prodline_table["Valeur Totale"].apply(format_currency)
        prodline_table["Quantité"] = prodline_table["Quantité"].apply(lambda x: f"{int(x)}")
        prodline_table["Commandes"] = prodline_table["Commandes"].apply(lambda x: f"{int(x)}")
        
        # Créer un style pour le DataFrame avec des couleurs par colonnes
        def highlight_columns_prodline(x):
            df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
            df_styler['Gamme de Produits'] = 'background-color: #e8f5e9; font-weight: bold'
            df_styler['Commandes'] = 'background-color: #e1f5fe'
            df_styler['Quantité'] = 'background-color: #fff8e1'
            df_styler['Valeur Totale'] = 'background-color: #fce4ec; font-weight: bold'
            return df_styler
        
        # Appliquer le style
        styled_prodline_df = prodline_table.style.apply(highlight_columns_prodline, axis=None)
        
        # Afficher le tableau avec les données
        st.dataframe(styled_prodline_df, use_container_width=True, hide_index=True)