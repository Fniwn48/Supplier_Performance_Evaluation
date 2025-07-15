import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from file1 import *

def part1_five(df, year, vendor_search):
    """
    Affiche les résultats des commandes pour une année et un fournisseur spécifiques.
    
    Parameters:
    -----------
    df : DataFrame
        Le DataFrame contenant les données de commandes
    year : int ou str
        L'année sélectionnée pour l'analyse
    vendor_search : str
        L'identifiant ou le nom du fournisseur recherché
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
    
    # Titre et description de la section
    st.markdown(f"""
        <div style="background-color:{color_palette['quaternary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
            <h4 style="color: white;text-align: center; margin: 0;">Analyse des Commandes pour {vendor_search} pour l'année {year}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # Filtrer les données pour l'année sélectionnée
    df_year = df[df['Year'] == int(year)]
    # Filtrer les données pour le fournisseur sélectionné
    df_year = df_year[
        (df_year["Nom du fournisseur"].str.contains(vendor_search, case=False)) | 
        (df_year["Fournisseur"].astype(str).str.contains(vendor_search, case=False))
]
      # Utiliser les mois sélectionnés stockés dans session_state
    df_year = df_year[df_year['Month'].isin(st.session_state.selected_months)]

    # Afficher les indicateurs clés (KPIs) pour le fournisseur sélectionné
    total_orders = df_year["Bons de commande"].nunique()
    total_materials = df_year["Matériel"].nunique()
    total_value = df_year["Valeur nette de la commande"].sum()
    
    # Affichage des KPIs dans 3 colonnes
    st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        display_metric_card("Nombre de commandes", total_orders, color="#3498db")
    with col2:
        display_metric_card("Nombre de références", total_materials, color="#2ecc71")
    with col3:
        display_metric_card("Valeur totale", format_currency(total_value), color="#f39c12")
    st.markdown('</div>', unsafe_allow_html=True) 
    # --- SECTION 2: COMPARAISON AVEC L'ANNÉE PRÉCÉDENTE ---
    st.markdown(f"""
    <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">Comparaison avec l'année précédente {int(year)-1}</h5>
    </div>
    """, unsafe_allow_html=True)

# Calculer les KPIs pour l'année précédente
previous_year = int(year) - 1
df_previous_year = df[df['Year'] == previous_year]

# DÉBOGAGE : Vérifier combien de lignes nous avons avant filtrage
print(f"Données pour {previous_year} avant filtrage fournisseur : {len(df_previous_year)} lignes")

df_previous_year = df_previous_year[
    (df_previous_year["Nom du fournisseur"].str.contains(vendor_search, case=False)) | 
    (df_previous_year["Fournisseur"].astype(str).str.contains(vendor_search, case=False))
]

# DÉBOGAGE : Vérifier combien de lignes nous avons après filtrage fournisseur
print(f"Données pour {previous_year} après filtrage fournisseur : {len(df_previous_year)} lignes")

# PROBLÈME POTENTIEL : Cette ligne peut vider le DataFrame
# Vérifiez d'abord si les mois sélectionnés existent dans l'année précédente
available_months_previous = df_previous_year['Month'].unique()
print(f"Mois disponibles pour {previous_year} : {available_months_previous}")
print(f"Mois sélectionnés : {st.session_state.selected_months}")

# Filtrer seulement par les mois qui existent dans l'année précédente
months_to_use = [month for month in st.session_state.selected_months if month in available_months_previous]
print(f"Mois à utiliser pour la comparaison : {months_to_use}")

if months_to_use:
    df_previous_year = df_previous_year[df_previous_year['Month'].isin(months_to_use)]
else:
    # Si aucun mois ne correspond, utilisez tous les mois disponibles ou affichez un message
    print("Aucun mois sélectionné n'est disponible pour l'année précédente")
    st.warning(f"Aucun mois sélectionné n'est disponible pour {previous_year}")

# DÉBOGAGE : Vérifier le DataFrame final
print(f"Données finales pour {previous_year} : {len(df_previous_year)} lignes")
if len(df_previous_year) > 0:
    print(f"Exemple de données :")
    print(df_previous_year[['Year', 'Month', 'Nom du fournisseur', 'Valeur nette de la commande']].head())

# KPIs année précédente
previous_total_orders = df_previous_year["Bons de commande"].nunique()
previous_total_materials = df_previous_year["Matériel"].nunique()
previous_total_value = df_previous_year["Valeur nette de la commande"].sum()

print(f"KPIs année précédente - Commandes: {previous_total_orders}, Matériels: {previous_total_materials}, Valeur: {previous_total_value}")

    # Calculer les variations avec gestion de la division par zéro
    if previous_total_orders > 0:
        orders_change = ((total_orders - previous_total_orders) / previous_total_orders * 100)
        orders_change_text = f"{orders_change:+.1f}%"
        orders_color = "green" if orders_change > 0 else "red" if orders_change < 0 else "gray"
    else:
        orders_change_text = "N/A"
        orders_color = "gray"
    
    if previous_total_materials > 0:
        materials_change = ((total_materials - previous_total_materials) / previous_total_materials * 100)
        materials_change_text = f"{materials_change:+.1f}%"
        materials_color = "green" if materials_change > 0 else "red" if materials_change < 0 else "gray"
    else:
        materials_change_text = "N/A"
        materials_color = "gray"
    
    if previous_total_value > 0:
        value_change = ((total_value - previous_total_value) / previous_total_value * 100)
        value_change_text = f"{value_change:+.1f}%"
        value_color = "green" if value_change > 0 else "red" if value_change < 0 else "gray"
    else:
        value_change_text = "N/A"
        value_color = "gray"
    
    # Affichage de la comparaison
    st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Nombre de commandes: {previous_total_orders} → {total_orders}</p>
                <h5 style="color:{orders_color}; margin:5px 0 0 0;">{orders_change_text}</h5>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Nombre de références: {previous_total_materials} → {total_materials}</p>
                <h5 style="color:{materials_color}; margin:5px 0 0 0;">{materials_change_text}</h5>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Valeur totale: {format_currency(previous_total_value)} → {format_currency(total_value)}</p>
                <h5 style="color:{value_color}; margin:5px 0 0 0;">{value_change_text}</h5>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
 
    # Analyse détaillée des produits pour ce fournisseur
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Détail des Matériels Commandés</h6>", unsafe_allow_html=True)
    
    # Regrouper les données par matériel
    material_summary = df_year.groupby(["Matériel", "Description du matériel", "Matériel du fournisseur"]).agg(
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
        "unite_achat": "Order Unit",
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
    top_products = df_year.groupby(["Matériel", "Matériel du fournisseur", "Description du matériel"]).agg(
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
            'text': f"Top 10 des produits pour l'année {year}",
            'font': {'size': 13, 'color': '#505050'},
            'y': 0.95
        },
        xaxis=dict(
            title='Produit',
            tickangle=-45
        ),
        yaxis=dict(
            title=dict(
                text='Valeur Totale (€)',
                font=dict(color='#FF7F00')
            ),
            tickfont=dict(color='#FF7F00')
        ),
        yaxis2=dict(
            title=dict(
                text='Nb Lignes',
                font=dict(color='#6A0DAD')
            ),
            tickfont=dict(color='#6A0DAD'),
            anchor='x',
            overlaying='y',
            side='right'
        ),
        # Le reste du code reste identique
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
    
    # Analyse par mois
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Évolution Mensuelle des Commandes</h6>", unsafe_allow_html=True)

    # Regrouper les données par mois
    monthly_data = df_year.groupby(["Month", "Month_Name"]).agg(
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
            'text': f"Évolution des commandes en {year} pour {vendor_search}",
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
                font=dict(color='#6A0DAD')  # Remplacer titlefont par font à l'intérieur de title
            ),
            tickfont=dict(color='#6A0DAD')
        ),
        yaxis2=dict(
            title=dict(
                text='Nombre de Commandes/Matériels',
                font=dict(color='#32CD32')  # Remplacer titlefont par font à l'intérieur de title
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

def camembert5(df,year,vendor_search):

    # Analyse par gamme (prodline)
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Répartition par Gamme de Produits</h6>", unsafe_allow_html=True)
     # Filtrer les données pour l'année sélectionnée
    df_year = df[df['Year'] == int(year)]
    # Filtrer les données pour le fournisseur sélectionné
    df_year = df_year[
    (df_year["Nom du fournisseur"].str.contains(vendor_search, case=False)) | 
    (df_year["Fournisseur"].astype(str).str.contains(vendor_search, case=False))
]
     # Utiliser les mois sélectionnés stockés dans session_state
    df_year = df_year[df_year['Month'].isin(st.session_state.selected_months)]

    # Regrouper les données par prodline
    prodline_summary = df_year.groupby("Prodline Name").agg(
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

    # Palette de couleurs sophistiquées - garder les mêmes couleurs que dans le code original
    color_palette = [
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
        marker=dict(colors=color_palette, line=dict(color='#FFFFFF', width=1.5)),
        textfont=dict(size=14),
        rotation=45
    )])

    # Mise en forme du graphique
    fig_pie.update_layout(
        title={
            'text': f"Répartition des produits par gamme pour {vendor_search} en {year}",
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
