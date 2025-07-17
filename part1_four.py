import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from file1 import *


def part1_four(df, vendor_search):
    """
    Affiche l'analyse complète des commandes pour un fournisseur spécifique,
    avec comparaison entre les années.
    
    Parameters:
    -----------
    df : DataFrame
        Le DataFrame contenant les données de commandes
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
    

    # Filtrer le DataFrame pour ne garder que les données du fournisseur sélectionné
    df = df[df['Nom du fournisseur'] == vendor_search].copy()

    # Cela doit être fait au début pour s'assurer que toutes les analyses concernent ce fournisseur
    df = df.copy()  # Créer une copie pour éviter de modifier le DataFrame original
    
    # Titre et description de la section
    st.markdown(f"""
        <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
            <h5 style="color: white;text-align: center; margin: 0;">Analyse des Commandes pour {vendor_search}</h5>
        </div>
        """, unsafe_allow_html=True)
    
    # Extraire l'année des dates pour l'analyse par année
    df['Année'] = pd.to_datetime(df['Date du document']).dt.year
    
    # Créer un tableau récapitulatif par année
    yearly_summary = df.groupby('Année').agg(
        nb_commandes=("Bons de commande", "nunique"),
        nb_produits=("Matériel", "nunique"),
        nb_lignes=("Bons de commande", "count"),
        qte_somme=("Order Quantity", "sum"),
        qte_min=("Order Quantity", "min"),
        qte_max=("Order Quantity", "max"),
        qte_moy=("Order Quantity", "mean"),
        valeur_totale=("Valeur nette de la commande", "sum")
    ).reset_index()
    
    # Trier par année
    yearly_summary = yearly_summary.sort_values(by="Année")
    
    # Formater les colonnes pour l'affichage
    yearly_summary_display = yearly_summary.copy()
    # Ajouter la colonne formatée sans supprimer l'originale pour l'instant
    yearly_summary_display["Valeur Totale"] = yearly_summary_display["valeur_totale"].apply(format_currency)


    # Renommer les colonnes
    yearly_summary_display = yearly_summary_display.rename(columns={
        "nb_commandes": "Nbre de commandes",
        "nb_produits": "Nbre de références",
        "nb_lignes": "Nombre de Lignes",
        "qte_min": "Qté Min",
        "qte_max": "Qté Max",
        "qte_moy": "Qté Moyenne",
        "qte_somme":"Qté Totale"
    })

    yearly_summary_display["Qté Moyenne"] = yearly_summary_display["Qté Moyenne"].apply(lambda x: f"{x:.1f}")  # Un chiffre après la virgule
    yearly_summary_display["Qté Totale"] = yearly_summary_display["Qté Totale"].apply(lambda x: f"{int(x)}")  # Pas de décimales
    yearly_summary_display["Qté Min"] = yearly_summary_display["Qté Min"].apply(lambda x: f"{int(x)}")  # Pas de décimales
    yearly_summary_display["Qté Max"] = yearly_summary_display["Qté Max"].apply(lambda x: f"{int(x)}")  # Pas de décimales
    # Vérifier que la colonne existe avant de la supprimer
    if "valeur_totale" in yearly_summary_display.columns:
        yearly_summary_display = yearly_summary_display.drop(columns=["valeur_totale"])
    
    
    # Style pour le tableau des années
    def highlight_columns_yearly(x):
        df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
        df_styler['Année'] = 'background-color: #e3f2fd; font-weight: bold;'
        df_styler['Nbre de commandes'] = 'background-color: #f1f8e9'
        df_styler['Nbre de références'] = 'background-color: #e8eaf6'
        df_styler['Nombre de Lignes'] = 'background-color: #e0f7fa'
        df_styler['Qté Totale'] = 'background-color: #f1f8e9'
        df_styler['Qté Min'] = 'background-color: #e8eaf6'
        df_styler['Qté Max'] = 'background-color: #ffebee'
        df_styler['Qté Moyenne'] = 'background-color: #e0f7fa'
        df_styler['Valeur Totale'] = 'background-color: #ffebee'
        return df_styler
    
    # Appliquer le style avec coloration des colonnes
    styled_yearly_df = yearly_summary_display.style.apply(highlight_columns_yearly, axis=None)
    
    # Afficher le tableau des résumés annuels
    st.markdown("<h6 style='color: #OOOOOO; margin-top: 20px;'>Résumé par Année</h6>", unsafe_allow_html=True)
    st.dataframe(styled_yearly_df, use_container_width=True, hide_index=True)
    
    # Ajouter l'information sur le mois pour les graphiques mensuels
    df['Mois'] = pd.to_datetime(df['Date du document']).dt.month
    df['Mois_Nom'] = pd.to_datetime(df['Date du document']).dt.strftime('%B')  # Nom du mois pour l'affichage
    
    # Grouper par année et mois pour les valeurs mensuelles
    monthly_values = df.groupby(['Année', 'Mois', 'Mois_Nom']).agg(
        valeur_totale=("Valeur nette de la commande", "sum"),
        nb_commandes=("Bons de commande", "nunique"),
        nb_produits=("Matériel", "nunique")
    ).reset_index()
    
    # Créer un graphique pour la valeur mensuelle par année
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Évolution Mensuelle de la Valeur des Commandes</h6>", unsafe_allow_html=True)
    
    fig_monthly_value = go.Figure()
    
    # Couleurs pour les différentes années (jusqu'à 10 années)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Ajouter une ligne pour chaque année
    for i, year in enumerate(sorted(monthly_values['Année'].unique())):
        year_data = monthly_values[monthly_values['Année'] == year]
        
        fig_monthly_value.add_trace(go.Scatter(
            x=year_data['Mois'],
            y=year_data['valeur_totale'],
            mode='lines+markers',
            name=f'Année {year}',
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate='<b>Mois %{x}</b><br>Valeur: %{y:,.2f} €<extra></extra>'
        ))
    
    # Configuration du layout
    fig_monthly_value.update_layout(
        xaxis=dict(
            title='Mois',
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        ),
        yaxis=dict(title='Valeur Totale (€)'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        template='plotly_white',
        hovermode="x unified"
    )
    
    # Afficher le graphique de valeur mensuelle
    st.plotly_chart(fig_monthly_value, use_container_width=True)
    
    # Graphique pour le nombre de commandes uniques par mois
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Évolution Mensuelle du Nombre de Commandes</h6>", unsafe_allow_html=True)
    
    fig_monthly_orders = go.Figure()
    
    # Ajouter une ligne pour chaque année
    for i, year in enumerate(sorted(monthly_values['Année'].unique())):
        year_data = monthly_values[monthly_values['Année'] == year]
        
        fig_monthly_orders.add_trace(go.Scatter(
            x=year_data['Mois'],
            y=year_data['nb_commandes'],
            mode='lines+markers',
            name=f'Année {year}',
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate='<b>Mois %{x}</b><br>Commandes: %{y}<extra></extra>'
        ))
    
    # Configuration du layout
    fig_monthly_orders.update_layout(
        xaxis=dict(
            title='Mois',
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        ),
        yaxis=dict(title='Nombre de Commandes Uniques'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        template='plotly_white',
        hovermode="x unified"
    )
    
    # Afficher le graphique de commandes mensuelles
    st.plotly_chart(fig_monthly_orders, use_container_width=True)
    
    # Graphique pour le nombre de produits uniques par mois
    st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Évolution Mensuelle du Nombre de Références</h6>", unsafe_allow_html=True)
    
    fig_monthly_products = go.Figure()
    
    # Ajouter une ligne pour chaque année
    for i, year in enumerate(sorted(monthly_values['Année'].unique())):
        year_data = monthly_values[monthly_values['Année'] == year]
        
        fig_monthly_products.add_trace(go.Scatter(
            x=year_data['Mois'],
            y=year_data['nb_produits'],
            mode='lines+markers',
            name=f'Année {year}',
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate='<b>Mois %{x}</b><br>Produits: %{y}<extra></extra>'
        ))
    
    # Configuration du layout
    fig_monthly_products.update_layout(
        xaxis=dict(
            title='Mois',
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        ),
        yaxis=dict(title='Nombre de Produits Uniques'),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        template='plotly_white',
        hovermode="x unified"
    )
    
    # Afficher le graphique de produits mensuels
    st.plotly_chart(fig_monthly_products, use_container_width=True)

    # Ajouter un expander avec les détails mensuels
    with st.expander("📊 Récapitulatif mensuel détaillé", expanded=False):
        # Préparation du tableau récapitulatif pour tous les mois et années
        all_monthly_data = []
        
        for year in sorted(monthly_values['Année'].unique()):
            st.markdown(f"<h4 style='color: #1E88E5;'>Année {year}</h4>", unsafe_allow_html=True)
            year_data = monthly_values[monthly_values['Année'] == year].sort_values(by='Mois')
            
            for _, row in year_data.iterrows():
                # Formater la valeur totale
                valeur_totale_formatted = f"{row['valeur_totale']:,.2f} €".replace(",", " ").replace(".", ",")
                
                # Créer une ligne descriptive avec les valeurs colorées
                st.markdown(
                    f"<b>{row['Mois_Nom']}</b> : "
                    f"<span style='color:#4285F4; font-weight:bold;'>{int(row['nb_commandes'])}</span> commandes, "
                    f"<span style='color:#DB4437; font-weight:bold;'>{int(row['nb_produits'])}</span> matériels, "
                    f"<span style='color:#9C27B0; font-weight:bold;'>{valeur_totale_formatted}</span>",
                    unsafe_allow_html=True
                )
            
            st.markdown("<hr>", unsafe_allow_html=True)
    
    # Obtenir d'abord la liste des produits par année
    products_by_year = {}
    all_years = sorted(df['Année'].unique())

    for year in all_years:
        products_by_year[year] = set(df[df['Année'] == year]['Matériel'].unique())

    # Trouver l'intersection (produits communs à toutes les années)
    if len(all_years) > 0:
        common_products = products_by_year[all_years[0]]
        for year in all_years[1:]:
            common_products = common_products.intersection(products_by_year[year])
    else:
        common_products = set()

    # Si des produits communs existent, créer le tableau des top 10
    if common_products and len(all_years) > 1:  # Seulement si nous avons plus d'une année
        st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Produits Commandés Chaque Année</h6>", unsafe_allow_html=True)
        
        # Filtrer le DataFrame pour ne garder que les produits communs
        common_products_df = df[df['Matériel'].isin(common_products)]
        
        # Grouper par produit et année pour avoir les statistiques par année
        product_stats = common_products_df.groupby(['Matériel', 'Description du matériel', 'Matériel du fournisseur', 'Année']).agg(
            nb_commandes=("Bons de commande", "nunique"),
            nb_lignes=("Bons de commande", "count"),
            unite_achat=("Order Unit", "first"), 
            valeur_totale=("Valeur nette de la commande", "sum"),
            quantite_totale=("Order Quantity", "sum")  # Ajout de la quantité totale
        ).reset_index()
        
        # Calculer la valeur moyenne par produit pour le tri
        avg_value_by_product = product_stats.groupby('Matériel')['valeur_totale'].mean().reset_index()
        avg_value_by_product.rename(columns={'valeur_totale': 'valeur_moyenne'}, inplace=True)
        
        # Trier par valeur moyenne et prendre tous les produits
        sorted_products = avg_value_by_product.sort_values(by='valeur_moyenne', ascending=False)
        
        # Filtrer les statistiques pour ne garder que les produits triés
        sorted_product_stats = product_stats[product_stats['Matériel'].isin(sorted_products['Matériel'])]
        
        # Tableau pivot pour avoir les années en colonnes
        pivot_table = pd.pivot_table(
            sorted_product_stats,
            index=['Matériel', 'Description du matériel', 'Matériel du fournisseur'],
            columns=['Année'],
            values=['nb_commandes', 'nb_lignes', 'valeur_totale', 'quantite_totale', 'unite_achat'],
            aggfunc={
                'nb_commandes': 'sum',
                'nb_lignes': 'sum',
                'valeur_totale': 'sum',
                'quantite_totale': 'sum',
                'unite_achat': 'first' 
            },
            fill_value=0
        )

        
        # Réorganiser le tableau pour l'affichage
        formatted_table = []
        
        for (material, desc, vendor_material), row in pivot_table.iterrows():
            # Calculer la valeur moyenne pour ce produit
            yearly_values = [row[('valeur_totale', year)] for year in all_years if ('valeur_totale', year) in row]
            avg_value = sum(yearly_values) / len(yearly_values) if yearly_values else 0
            
            product_data = {
                'Code Produit': material,
                'Description': desc,
                'Réf. Fournisseur': vendor_material,
                'Valeur Moyenne': format_currency(avg_value),
                'Unité d\'Achat': row[('unite_achat', all_years[0])]  # Ajout de l’unité à la 1re année

            }
            
            # Ajouter les données pour chaque année
            for year in all_years:
                try:
                    product_data[f'Commandes {year}'] = int(row[('nb_commandes', year)])
                    product_data[f'Lignes {year}'] = int(row[('nb_lignes', year)])
                    product_data[f'Valeur {year}'] = format_currency(row[('valeur_totale', year)])
                    product_data[f'Quantité {year}'] = f"{int(row[('quantite_totale', year)]):,}".replace(',', ' ')  # Format avec espace comme séparateur de milliers
                except (KeyError, TypeError):
                    product_data[f'Commandes {year}'] = 0
                    product_data[f'Lignes {year}'] = 0
                    product_data[f'Valeur {year}'] = format_currency(0)
                    product_data[f'Quantité {year}'] = "0"
            
            formatted_table.append(product_data)
        
        # Créer un DataFrame à partir de la liste formatée
        formatted_df = pd.DataFrame(formatted_table)
        
        # Trier le DataFrame par la valeur moyenne (décroissante)
        formatted_df = formatted_df.sort_values(by='Valeur Moyenne', ascending=False, key=lambda x: x.str.replace(' ', '').str.replace('€', '').str.replace(',', '.').astype(float))
        
        # Style pour le tableau des produits communs
        def highlight_columns_products(df):
            # Créer un styler avec des cellules vides
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            
            # Appliquer des styles par colonne
            styles['Code Produit'] = 'background-color: #e3f2fd; font-weight: bold;'
            styles['Description'] = 'background-color: #f1f8e9'
            styles['Réf. Fournisseur'] = 'background-color: #e8eaf6'
            styles['Valeur Moyenne'] = 'background-color: #fff9c4; font-weight: bold;'
            styles['Unité d\'Achat'] = 'background-color: #e0f7fa; font-style: italic;'


            
            # Appliquer des styles pour les colonnes d'années
            for year in all_years:
                col_commandes = f'Commandes {year}'
                col_lignes = f'Lignes {year}'
                col_valeur = f'Valeur {year}'
                col_quantite = f'Quantité {year}'
                
                if col_commandes in df.columns:
                    styles[col_commandes] = 'background-color: #e0f7fa'
                if col_lignes in df.columns:
                    styles[col_lignes] = 'background-color: #f3e5f5'
                if col_valeur in df.columns:
                    styles[col_valeur] = 'background-color: #ffebee; font-weight: bold;'
                if col_quantite in df.columns:
                    styles[col_quantite] = 'background-color: #e8f5e9; font-weight: bold;'
            
            return styles
        
        # Appliquer le style
        styled_products_df = formatted_df.style.apply(highlight_columns_products, axis=None)
        
        # Afficher le tableau
        st.dataframe(styled_products_df, use_container_width=True, hide_index=True)
        
    elif len(all_years) <= 1:
        st.info("Analyse des produits communs non disponible - données présentes pour une seule année.")
    else:
        st.info("Aucun produit commun à toutes les années n'a été trouvé pour ce fournisseur.")


def camembert4(df,vendor_search):

     # Filtrer le DataFrame pour ne garder que les données du fournisseur sélectionné
    df = df[df['Nom du fournisseur'] == vendor_search].copy()

    # Cela doit être fait au début pour s'assurer que toutes les analyses concernent ce fournisseur
    df = df.copy()  
    
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

    # Palette de couleurs (utilise les couleurs du premier code)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Créer le camembert
    fig_pie = go.Figure(data=[go.Pie(
        labels=prodline_summary['Prodline Name'],
        values=prodline_summary['valeur_totale'],
        text=prodline_summary['labels'],
        hoverinfo='text',
        textinfo='percent',
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='#FFFFFF', width=1.5)),
        textfont=dict(size=14),
        rotation=45
    )])

    # Mise en forme du graphique
    fig_pie.update_layout(
        title={
            'text': f"Répartition des produits par gamme pour {vendor_search}",
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
            df_styler['Gamme de Produits'] = 'background-color: #e3f2fd; font-weight: bold;'
            df_styler['Commandes'] = 'background-color: #f1f8e9'
            df_styler['Quantité'] = 'background-color: #e8eaf6'
            df_styler['Valeur Totale'] = 'background-color: #ffebee; font-weight: bold;'
            return df_styler
        
        # Appliquer le style
        styled_prodline_df = prodline_table.style.apply(highlight_columns_prodline, axis=None)
        
        # Afficher le tableau avec les données
        st.dataframe(styled_prodline_df, use_container_width=True, hide_index=True)
