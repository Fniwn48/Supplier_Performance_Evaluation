import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from file1 import *


def part1_one(df, year):
    """
    Affiche les résultats des commandes pour une année spécifique.
    
    Parameters:
    -----------
    df : DataFrame
        Le DataFrame contenant les données de commandes
    year : int ou str
        L'année sélectionnée pour l'analyse
    """
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
    
    st.markdown(f"""
        <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
            <h4 style="color: white;text-align: center; margin: 0;">Analyse des Commandes pour l'année {year}</h4>
        </div>
        """, unsafe_allow_html=True)


    df = df[df['Year'] ==year]
    # Vérifier si le dataframe est vide après le second filtre
    if df.empty:
        st.warning(f"Aucune donnée disponible pour l'année {year}")
        return
   
    
    # Afficher les indicateurs clés (KPIs) pour l'année sélectionnée
    total_orders = df["Bons de commande"].nunique()
    total_vendors = df["Fournisseur"].nunique()
    total_materials = df["Matériel"].nunique()
    total_value = df["Valeur nette de la commande"].sum()
    
    # Affichage des KPIs dans 4 colonnes avec nouvelles couleurs
    st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        display_metric_card("Bons de commande", total_orders, color="#3498db")
    with col2:
        display_metric_card("Fournisseurs", total_vendors, color="#e74c3c")
    with col3:
        display_metric_card("Matériels uniques", total_materials, color="#2ecc71")
    with col4:
        display_metric_card("Valeur totale", format_currency(total_value), color="#f39c12")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analyse par matériel
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Détail des Matériels Commandés</h6>", unsafe_allow_html=True)
    
    # Regrouper les données par matériel
    material_summary = df.groupby(["Matériel", "Description du matériel", "Matériel du fournisseur", "Nom du fournisseur"]).agg(
        nb_commandes=("Bons de commande", "nunique"),
        nb_lignes=("Bons de commande", "count"),
        unite_achat=("Order Unit", "first"), 
        qte_somme=("Order Quantity", "sum"),
        qte_min=("Order Quantity", "min"),
        qte_max=("Order Quantity", "max"),
        qte_moy=("Order Quantity", "mean"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()

    # Trier par valeur totale (décroissant)
    material_summary = material_summary.sort_values(by="valeur_totale", ascending=False)

    # Renommer les colonnes pour l'affichage
    material_summary = material_summary.rename(columns={
        "Matériel": "Matériel",
        "Description du matériel": "Description",
        "Matériel du fournisseur": "Réf. Fournisseur",
        "Nom du fournisseur": "Fournisseur",
        "nb_commandes": "Nb Commandes",
        "nb_lignes": "Nb Lignes",
        "unite_achat": "Order Unit",
        "qte_somme": "Qté Totale",
        "qte_min": "Qté Min",
        "qte_max": "Qté Max",
        "qte_moy": "Qté Moyenne",
        "valeur_totale": "Valeur Totale"
    })

    # Formater la colonne de valeur totale
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
        df_styler['Fournisseur'] = 'background-color: #fff3e0'
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
    
    # Analyse par mois
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Évolution Mensuelle des Commandes</h6>", unsafe_allow_html=True)

    # Regrouper les données par mois
    monthly_data = df.groupby(["Month", "Month_Name"]).agg(
        nb_commandes=("Bons de commande", "nunique"),
        nb_materials=("Matériel", "nunique"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()

    # Trier par mois
    monthly_data = monthly_data.sort_values(by="Month")

    # Créer le graphique d'évolution mensuelle
    fig = go.Figure()

    # Ajouter les barres pour la valeur totale (axe Y gauche)
    fig.add_trace(go.Bar(
        x=monthly_data["Month_Name"],
        y=monthly_data["valeur_totale"],
        name='Valeur Totale (€)',
        marker=dict(color='#6A0DAD'),
        opacity=0.85,
        hovertemplate='<b>%{x}</b><br>Valeur: %{y:,.2f} €<extra></extra>'
    ))

    # Ajouter une ligne pour le nombre de matériels (axe Y droit)
    fig.add_trace(go.Scatter(
        x=monthly_data["Month_Name"],
        y=monthly_data["nb_materials"],
        mode='lines+markers',
        name='Nb Matériels',
        line=dict(color='#FF7F00', width=3),
        marker=dict(size=9, symbol='diamond'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Matériels: %{y}<extra></extra>'
    ))

    # Ajouter une ligne pour le nombre de commandes (axe Y droit)
    fig.add_trace(go.Scatter(
        x=monthly_data["Month_Name"],
        y=monthly_data["nb_commandes"],
        mode='lines+markers',
        name='Nb Commandes',
        line=dict(color='#32CD32', width=3, dash='dashdot'),
        marker=dict(size=9, symbol='circle'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Commandes: %{y}<extra></extra>'
    ))

    # Configuration des axes et du layout
    fig.update_layout(
        title={
            'text': f"Évolution des commandes en {year}",
            'font': {'size': 13, 'color': '#505050'},
            'y': 0.95
        },
        xaxis=dict(
            title='Mois',
            tickangle=-45
        ),
        yaxis=dict(
            title=dict(
                text='Valeur (€)',
                font=dict(color='#6A0DAD')
            ),
            tickfont=dict(color='#6A0DAD')
        ),
        yaxis2=dict(
            title=dict(
                text='Nombre de Commandes/Matériels',
                font=dict(color='#32CD32')
            ),
            tickfont=dict(color='#32CD32'),
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
    st.plotly_chart(fig, use_container_width=True)

    # Ajouter un expander avec le tableau récapitulatif
    with st.expander("📊 Récapitulatif mensuel détaillé", expanded=False):
        # Préparation du tableau récapitulatif
        summary_table = monthly_data.copy()
        
        # Renommer les colonnes
        summary_table = summary_table.rename(columns={
            "Month_Name": "Mois", 
            "nb_commandes": "Commandes", 
            "nb_materials": "Matériels", 
            "valeur_totale": "Valeur Totale"
        })
        
        for _, row in summary_table.iterrows():
            # Formater la valeur totale
            valeur_totale_formatted = f"{row['Valeur Totale']:,.2f} €".replace(",", " ").replace(".", ",")
            
            # Créer une ligne descriptive avec les valeurs colorées
            st.markdown(
                f"<b>{row['Mois']}</b> : "
                f"<span style='color:#4285F4; font-weight:bold;'>{int(row['Commandes'])}</span> commandes, "
                f"<span style='color:#DB4437; font-weight:bold;'>{int(row['Matériels'])}</span> matériels, "
                f"<span style='color:#9C27B0; font-weight:bold;'>{valeur_totale_formatted}</span>",
                unsafe_allow_html=True
            )
            
    # Analyse par fournisseur
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Top 10 des Fournisseurs</h6>", unsafe_allow_html=True)
    
    # Regrouper les données par fournisseur
    vendor_summary = df.groupby(["Fournisseur", "Nom du fournisseur"]).agg(
        nb_commandes=("Bons de commande", "nunique"),
        nb_materials=("Matériel", "nunique"),
        qte_somme=("Order Quantity", "sum"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()
    
    # Trier par valeur totale et prendre les 10 premiers
    top_vendors = vendor_summary.sort_values(by="valeur_totale", ascending=False).head(10)
    
    # Créer le graphique pour les fournisseurs
    fig_vendors = px.bar(
        top_vendors,
        x="Nom du fournisseur",
        y="valeur_totale",
        # text=top_vendors["valeur_totale"].apply(lambda x: f"{x:,.2f} €".replace(",", " ").replace(".", ",")),
        color="nb_commandes",
        color_continuous_scale=px.colors.sequential.Viridis,
        title=f"Top 10 des fournisseurs en {year} par valeur de commande",
        labels={
            "Nom du fournisseur": "Fournisseur",
            "valeur_totale": "Valeur Totale (€)",
            "qte_somme": "Qté Totale",
            "nb_commandes": "Nombre de Commandes"
        },
        height=500
    )
    
    # Mise en forme du graphique
    fig_vendors.update_layout(
        xaxis_tickangle=-45,
        yaxis=dict(title='Valeur Totale (€)'),
        coloraxis_colorbar=dict(title='Nb Commandes'),
        template='plotly_white'
    )
    
    # Afficher le graphique
    st.plotly_chart(fig_vendors, use_container_width=True)
    
    # Tableau détaillé des fournisseurs
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Détail par Fournisseur</h6>", unsafe_allow_html=True)

    # Renommer les colonnes pour l'affichage
    vendor_display = vendor_summary.rename(columns={
        "Fournisseur": "ID Fournisseur",
        "Nom du fournisseur": "Nom Fournisseur",
        "nb_commandes": "Nb Commandes",
        "nb_materials": "Nb Matériels",
        "qte_somme": "Qté Totale",
        "valeur_totale": "Valeur Totale"
    })
    vendor_display['ID Fournisseur'] = vendor_display['ID Fournisseur'].astype(int)


    # Créer une copie pour le tri avant le formatage
    vendor_display_sorted = vendor_display.sort_values(by="Valeur Totale", ascending=False)

    # Maintenant, formater la colonne après le tri
    vendor_display_sorted["Valeur Totale"] = vendor_display_sorted["Valeur Totale"].apply(format_currency)
    vendor_display_sorted["Qté Totale"] = vendor_display_sorted["Qté Totale"].apply(lambda x: f"{int(x)}")  # Pas de décimales


    # Créer un style pour l'ensemble du DataFrame des fournisseurs avec des couleurs par colonnes
    def highlight_columns_vendor(x):
        df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
        df_styler['ID Fournisseur'] = 'background-color: #e8f5e9'
        df_styler['Nom Fournisseur'] = 'background-color: #fff8e1' 
        df_styler['Nb Commandes'] = 'background-color: #e1f5fe'
        df_styler['Nb Matériels'] = 'background-color: #f5f5f5'
        df_styler['Qté Totale'] = 'background-color: #fff8e1'
        df_styler['Valeur Totale'] = 'background-color: #fce4ec'
        return df_styler

    # Appliquer le style avec coloration des colonnes
    styled_vendor_df = vendor_display_sorted.style.apply(highlight_columns_vendor, axis=None)

    # Afficher le tableau avec les données
    st.dataframe(styled_vendor_df, use_container_width=True, hide_index=True)



def camembert1(df,year):

    
    df = df[df['Year'] ==year]
    # Vérifier si le dataframe est vide après le second filtre
    if df.empty:
        st.warning(f"Aucune donnée disponible pour l'année {year}")
        return
   
    # Analyse par gamme (prodline)
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

    # Palette de couleurs sophistiquées
    color_palette = [
        '#2E4057', '#083D77', '#4D6A92', '#006E90', '#4F86C6', 
        '#5C4A72', '#7E5A9B', '#9B5094', '#B64E97', '#D34B99',
        '#7E7B52', '#938B4A', '#A89A42', '#BDAA3A', '#D1BB32'
    ]

    # Créer le camembert
    fig_pie = go.Figure(data=[go.Pie(
        labels=prodline_summary['Prodline Name'],
        values=prodline_summary['valeur_totale'],
        text=prodline_summary['labels'],
        hoverinfo='text',
        textinfo='percent',
        hole=0.4,
        marker=dict(colors=color_palette, line=dict(color='#FFFFFF', width=1.5)),
        textfont=dict(size=14),
        rotation=45
    )])

    # Mise en forme du graphique
    fig_pie.update_layout(
        title={
            'text': f"Répartition des produits par gamme en {year}",
            'font': {'size': 13, 'color': '#505050'},
            'y': 0.95
        },
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.7,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        ),
        height=650,
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