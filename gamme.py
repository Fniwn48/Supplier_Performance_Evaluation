import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def analyser_gamme(df, gamme_selectionnee):
    """
    Analyse d'une gamme de matériel spécifique dans un dataframe.
    
    Args:
        df (pandas.DataFrame): Dataframe avec les colonnes requises
        gamme_selectionnee (str): Nom de la gamme à analyser
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
    # Filtrer le dataframe pour ne garder que la gamme sélectionnée
    df_gamme = df[df['Prodline Name'] == gamme_selectionnee].copy()
    
    if df_gamme.empty:
        st.error(f"Aucune donnée trouvée pour la gamme '{gamme_selectionnee}'")
        return
    
    # S'assurer que les dates sont au bon format
    df_gamme['Date du document'] = pd.to_datetime(df_gamme['Date du document'])
    
    # Extraire l'année et le mois pour les analyses
    df_gamme['Année'] = df_gamme['Date du document'].dt.year
    df_gamme['Mois'] = df_gamme['Date du document'].dt.month
    df_gamme['Mois-Nom'] = df_gamme['Date du document'].dt.strftime('%b')
    
    # Convertir les colonnes numériques si nécessaire
    cols_numeriques = ['Valeur nette de la commande', 'Order Quantity']
    for col in cols_numeriques:
        if df_gamme[col].dtype == 'object':
            df_gamme[col] = pd.to_numeric(df_gamme[col], errors='coerce')
    
    # Afficher le titre de la section
      
    st.markdown(f"""
        <div style="background-color:{color_palette['positive']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
            <h4 style="color: white;text-align: center; margin: 0;">Analyse de la gamme: {gamme_selectionnee}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    # ------------------- TABLEAU 1 : ANALYSE PAR ANNÉE -------------------
    st.markdown("<h5 style='color: #000000; margin-top: 20px;'>Analyse par année</h5>", unsafe_allow_html=True)
    
    # Agréger les données par année
    yearly_data = df_gamme.groupby('Année').agg(
        Valeur_Totale=('Valeur nette de la commande', 'sum'),
        Nombre_Commandes=('Bons de commande', 'nunique'),
        Nombre_Materiels=('Matériel', 'nunique'),
        Quantite_Totale=('Order Quantity', 'sum'),
        Quantite_Min=('Order Quantity', 'min'),
        Quantite_Max=('Order Quantity', 'max'),
        Quantite_Moyenne=('Order Quantity', 'mean')
    ).reset_index()
    
    # Convertir les quantités en entier (pour celles qui doivent être des entiers)
    int_columns = ['Quantite_Totale', 'Quantite_Min', 'Quantite_Max']
    for col in int_columns:
        yearly_data[col] = yearly_data[col].astype(int)
    
    # Arrondir uniquement les valeurs de moyenne à 1 chiffre après la virgule
    yearly_data['Quantite_Moyenne'] = yearly_data['Quantite_Moyenne'].round(1)
    
    # Convertir l'année en entier
    yearly_data['Année'] = yearly_data['Année'].astype(int)
        
    # Fonction pour appliquer un style sophistiqué au tableau avec toutes les colonnes colorées
    def style_yearly_table(df):
        # On utilise une fonction pour formater les valeurs monétaires avec séparateurs d'espace
        def format_currency(x):
            return f"{x:,.1f} €".replace(',', ' ') if pd.notnull(x) else ""
        
        # On utilise une fonction pour formater les nombres avec séparateurs d'espace
        def format_number(x):
            return f"{x:,}".replace(',', ' ') if pd.notnull(x) else ""
        
        return (df.style
                .background_gradient(cmap='Blues', subset=['Année'])
                .background_gradient(cmap='Greens', subset=['Valeur_Totale'])
                .background_gradient(cmap='Reds', subset=['Nombre_Commandes'])
                .background_gradient(cmap='Purples', subset=['Nombre_Materiels'])
                .background_gradient(cmap='Oranges', subset=['Quantite_Totale'])
                .background_gradient(cmap='YlGn', subset=['Quantite_Min'])
                .background_gradient(cmap='YlOrBr', subset=['Quantite_Max'])
                .background_gradient(cmap='PuBu', subset=['Quantite_Moyenne'])
                .format({
                    'Valeur_Totale': format_currency,
                    'Quantite_Totale': format_number,
                    'Quantite_Min': format_number,
                    'Quantite_Max': format_number,
                    'Quantite_Moyenne': '{:.1f}'
                })
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4a4a4a'), 
                                               ('color', 'white'),
                                               ('font-weight', 'bold'),
                                               ('text-align', 'center')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]},
                    {'selector': '.index_name', 'props': [('display', 'none')]},  # Masquer l'en-tête d'index
                    {'selector': '.row_heading', 'props': [('display', 'none')]},  # Masquer les indices de ligne
                ])
                .hide(axis="index")  # Pour supprimer complètement l'index
               )
    
    # Remplacer st.write par st.dataframe avec hide_index=True
    st.dataframe(style_yearly_table(yearly_data), use_container_width=True, hide_index=True)
    
    # ------------------- GRAPHIQUE LINÉAIRE PAR MOIS ET ANNÉE -------------------
    st.markdown("<h5 style='color: #000000; margin-top: 20px;'>Évolution mensuelle par année</h5>", unsafe_allow_html=True)

    
    # Agréger les données par année et mois
    monthly_data = df_gamme.groupby(['Année', 'Mois']).agg(
        Valeur_Totale=('Valeur nette de la commande', 'sum'),
        Quantite_Totale=('Order Quantity', 'sum'),
        Nombre_Materiels=('Matériel', 'nunique')
    ).reset_index()
    
    # Convertir les quantités en entier
    monthly_data['Quantite_Totale'] = monthly_data['Quantite_Totale'].astype(int)
    
    # Convertir l'année en entier
    monthly_data['Année'] = monthly_data['Année'].astype(int)
    monthly_data['Année_str'] = monthly_data['Année'].astype(str)
    
    # Créer un graphique linéaire interactif avec Plotly
    fig = px.line(
        monthly_data, 
        x='Mois', 
        y='Valeur_Totale',
        color='Année_str',
        labels={'Mois': 'Mois', 'Valeur_Totale': 'Valeur Totale (€)', 'Année_str': 'Année'},
        title=f'Évolution mensuelle de la valeur totale pour la gamme {gamme_selectionnee}',
        markers=True,
        hover_data=['Quantite_Totale', 'Nombre_Materiels']
    )
    
    # Améliorer le design du graphique
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
        ),
        plot_bgcolor='rgba(240, 240, 240, 0.8)',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )
    
    # Ajuster les marges
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    
    # Ajouter des lignes de grille
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200, 200, 200, 0.2)')
    
    # Afficher le graphique
    st.plotly_chart(fig, use_container_width=True)
    
    # ------------------- TABLEAU 2 : ANALYSE PAR FOURNISSEUR -------------------
    st.markdown("<h5 style='color: #000000; margin-top: 20px;'>Analyse par fournisseur</h5>", unsafe_allow_html=True)

    # Créer une fonction pour agréger les données par année pour chaque fournisseur
    def create_supplier_pivot(df_filtered):
        # Grouper par fournisseur et année
        supplier_data = df_filtered.groupby(['Nom du fournisseur', 'Fournisseur', 'Année']).agg(
            Valeur_Totale=('Valeur nette de la commande', 'sum'),
            Quantite=('Order Quantity', 'sum'),
            Nombre_Materiels=('Matériel', 'nunique')
        ).reset_index()
        
        # Convertir la quantité en entier
        supplier_data['Quantite'] = supplier_data['Quantite'].astype(int)
        
        # Créer des colonnes dynamiques pour chaque année
        supplier_pivot = pd.pivot_table(
            supplier_data,
            index=['Nom du fournisseur', 'Fournisseur'],
            columns='Année',
            values=['Valeur_Totale', 'Quantite', 'Nombre_Materiels'],
            aggfunc='sum',
            fill_value=0
        )
        
        # Aplatir les noms de colonnes multi-index
        supplier_pivot.columns = [f"{col[0]}_{col[1]}" for col in supplier_pivot.columns]
        supplier_pivot = supplier_pivot.reset_index()
        
        # Calculer la valeur moyenne sur toutes les années
        val_cols = [col for col in supplier_pivot.columns if col.startswith('Valeur_Totale_')]
        if val_cols:
            supplier_pivot['Valeur_Moyenne'] = supplier_pivot[val_cols].mean(axis=1).round(1)
            
            # Trier par valeur moyenne décroissante
            supplier_pivot = supplier_pivot.sort_values('Valeur_Moyenne', ascending=False)
        
        # Vérifier si la colonne Fournisseur est présente et convertir en entier si possible
        if 'Fournisseur' in supplier_pivot.columns:
            try:
                supplier_pivot['Fournisseur'] = supplier_pivot['Fournisseur'].astype(int)
            except (ValueError, TypeError):
                # Si la conversion échoue, garder la colonne telle quelle
                pass
            
        # Convertir les colonnes de quantité en entier
        quant_cols = [col for col in supplier_pivot.columns if col.startswith('Quantite_')]
        for col in quant_cols:
            supplier_pivot[col] = supplier_pivot[col].astype(int)
        
        return supplier_pivot
    
    # Créer le tableau des fournisseurs
    supplier_table = create_supplier_pivot(df_gamme)
    
    # Appliquer un style sophistiqué
    def style_supplier_table(df):
        # Identifier les colonnes
        all_cols = df.columns.tolist()
        val_cols = [col for col in all_cols if col.startswith('Valeur_Totale_')]
        quant_cols = [col for col in all_cols if col.startswith('Quantite_')]
        mat_cols = [col for col in all_cols if col.startswith('Nombre_Materiels_')]
        name_cols = ['Nom du fournisseur', 'Fournisseur']
        
        # Fonctions pour formater les nombres avec séparateurs d'espace
        def format_currency(x):
            return f"{x:,.1f} €".replace(',', ' ') if pd.notnull(x) else ""
        
        def format_number(x):
            return f"{x:,}".replace(',', ' ') if pd.notnull(x) else ""
        
        # Créer un objet de style
        styler = df.style
        
        # Appliquer des couleurs aux colonnes numériques
        for col in val_cols + quant_cols + mat_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if col in val_cols:
                    styler = styler.background_gradient(cmap='Blues', subset=[col], vmin=0)
                elif col in quant_cols:
                    styler = styler.background_gradient(cmap='Greens', subset=[col], vmin=0)
                elif col in mat_cols:
                    styler = styler.background_gradient(cmap='Purples', subset=[col], vmin=0)
        
        # Pour la colonne "Nom du fournisseur" (non numérique)
        if 'Nom du fournisseur' in df.columns:
            styler = styler.map(lambda x: 'background-color: #E1F5FE', subset=['Nom du fournisseur'])

        # Pour la colonne "Fournisseur" (même si numérique, appliquer une couleur fixe)
        if 'Fournisseur' in df.columns:
            styler = styler.map(lambda x: 'background-color: #FFFDE7', subset=['Fournisseur'])
        
        # Appliquer un gradient de couleur à la valeur moyenne seulement si c'est numérique
        if 'Valeur_Moyenne' in df.columns and pd.api.types.is_numeric_dtype(df['Valeur_Moyenne']):
            styler = styler.background_gradient(cmap='RdYlGn', subset=['Valeur_Moyenne'])
        
        # Préparer le dictionnaire de formatage
        format_dict = {}
        for col in df.columns:
            if col in name_cols:
                continue
            elif col.startswith('Valeur_') or 'Valeur_Moyenne' == col:
                format_dict[col] = format_currency
            else:
                format_dict[col] = format_number
        
        return (styler
                .format(format_dict)
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4a4a4a'), 
                                               ('color', 'white'),
                                               ('font-weight', 'bold'),
                                               ('text-align', 'center')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]},
                    {'selector': '.index_name', 'props': [('display', 'none')]},  # Masquer l'en-tête d'index
                    {'selector': '.row_heading', 'props': [('display', 'none')]},  # Masquer les indices de ligne
                ])
                .hide(axis="index")  # Pour supprimer complètement l'index
               )
    
    st.dataframe(style_supplier_table(supplier_table), use_container_width=True, hide_index=True)
    
    # ------------------- TABLEAU 3 : ANALYSE PAR MATÉRIEL -------------------

    st.markdown("<h5 style='color: #000000; margin-top: 20px;'>Analyse par Matériel</h5>", unsafe_allow_html=True)
    
    # Créer une fonction pour agréger les données par année pour chaque matériel
    def create_material_pivot(df_filtered):
        # Grouper par matériel et année
        material_data = df_filtered.groupby(['Matériel', 'Matériel du fournisseur', 
                                             'Description du matériel', 'Nom du fournisseur', 'Order Unit','Année']).agg(
            Valeur_Totale=('Valeur nette de la commande', 'sum'),
            Quantite=('Order Quantity', 'sum')
        ).reset_index()
        
        # Convertir la quantité en entier
        material_data['Quantite'] = material_data['Quantite'].astype(int)
        
        # Créer des colonnes dynamiques pour chaque année
        material_pivot = pd.pivot_table(
            material_data,
            index=['Matériel', 'Matériel du fournisseur', 'Description du matériel', 'Nom du fournisseur', 'Order Unit'],
            columns='Année',
            values=['Valeur_Totale', 'Quantite'],
            aggfunc='sum',
            fill_value=0
        )
        
        # Aplatir les noms de colonnes multi-index
        material_pivot.columns = [f"{col[0]}_{col[1]}" for col in material_pivot.columns]
        material_pivot = material_pivot.reset_index()
        
        # Calculer la valeur moyenne sur toutes les années
        val_cols = [col for col in material_pivot.columns if col.startswith('Valeur_Totale_')]
        if val_cols:
            material_pivot['Valeur_Moyenne'] = material_pivot[val_cols].mean(axis=1).round(1)
            
            # Trier par valeur moyenne décroissante
            material_pivot = material_pivot.sort_values('Valeur_Moyenne', ascending=False)
            
        # Convertir les colonnes de quantité en entier
        quant_cols = [col for col in material_pivot.columns if col.startswith('Quantite_')]
        for col in quant_cols:
            material_pivot[col] = material_pivot[col].astype(int)
        
        return material_pivot
    
    # Créer le tableau des matériels
    material_table = create_material_pivot(df_gamme)
    
    # Appliquer un style sophistiqué
    def style_material_table(df):
        # Identifier toutes les colonnes pour appliquer des couleurs
        all_cols = df.columns.tolist()
        val_cols = [col for col in all_cols if col.startswith('Valeur_Totale_')]
        quant_cols = [col for col in all_cols if col.startswith('Quantite_')]
        info_cols = ['Matériel', 'Matériel du fournisseur', 'Description du matériel', 'Nom du fournisseur','Order Unit']
        
        # Fonctions pour formater les nombres avec séparateurs d'espace
        def format_currency(x):
            return f"{x:,.1f} €".replace(',', ' ') if pd.notnull(x) else ""
        
        def format_number(x):
            return f"{x:,}".replace(',', ' ') if pd.notnull(x) else ""
        
        # Créer un objet de style
        styler = df.style
        
        # Appliquer des couleurs aux colonnes numériques
        for col in val_cols + quant_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                if col in val_cols:
                    styler = styler.background_gradient(cmap='Blues', subset=[col], vmin=0)
                elif col in quant_cols:
                    styler = styler.background_gradient(cmap='Greens', subset=[col], vmin=0)
        
        # Couleurs fixes pour les colonnes d'information
        for col, color in [
            ('Matériel', '#FFF3E0'),              # Orange pâle
            ('Matériel du fournisseur', '#E8F5E9'),  # Vert pâle
            ('Description du matériel', '#F3E5F5'),  # Violet pâle
            ('Nom du fournisseur', '#E1F5FE'),      # Bleu pâle
            ('Order Unit', '#E1F5FE')      # Bleu pâle

        ]:
            if col in df.columns:
                styler = styler.map(lambda x: f'background-color: {color}', subset=[col])
                        
        # Appliquer un gradient de couleur à la valeur moyenne seulement si c'est numérique
        if 'Valeur_Moyenne' in df.columns and pd.api.types.is_numeric_dtype(df['Valeur_Moyenne']):
            styler = styler.background_gradient(cmap='RdYlGn', subset=['Valeur_Moyenne'])
        
        # Préparer le dictionnaire de formatage
        format_dict = {}
        for col in df.columns:
            if col in info_cols:
                continue
            elif col.startswith('Valeur_') or 'Valeur_Moyenne' == col:
                format_dict[col] = format_currency
            else:
                format_dict[col] = format_number
        
        return (styler
                .format(format_dict)
                .set_properties(**{'text-align': 'center'})
                .set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4a4a4a'), 
                                               ('color', 'white'),
                                               ('font-weight', 'bold'),
                                               ('text-align', 'center')]},
                    {'selector': 'td', 'props': [('text-align', 'center')]},
                    {'selector': '.index_name', 'props': [('display', 'none')]},  # Masquer l'en-tête d'index
                    {'selector': '.row_heading', 'props': [('display', 'none')]},  # Masquer les indices de ligne
                ])
                .hide(axis="index")  # Pour supprimer complètement l'index
               )
    
    st.dataframe(style_material_table(material_table), use_container_width=True, hide_index=True)

    