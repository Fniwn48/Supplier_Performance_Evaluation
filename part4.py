import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

def part_four(df, selected_supplier):
    """
    Analyse des performances d'un fournisseur spécifique
    
    Args:
        df: DataFrame contenant les données complètes
        selected_supplier: Nom ou ID du fournisseur à analyser
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
    

    # Filtrer les données pour le fournisseur sélectionné
    supplier_data = df[(df['Nom du fournisseur'] == selected_supplier) | 
                     (df['Fournisseur'] == selected_supplier)].copy()
    
    if supplier_data.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {selected_supplier}")
        return
    
    # Récupérer le nom et l'ID du fournisseur
    supplier_name = supplier_data['Nom du fournisseur'].iloc[0]
    supplier_id = supplier_data['Fournisseur'].iloc[0]
    
    # Utiliser un style personnalisé pour l'en-tête
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 10px; border-radius: 10px;">
        <h4 style="color: white; text-align: center;">Analyse du fournisseur: {supplier_name} (ID: {supplier_id})</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculer les délais pour les commandes (le délai le plus long parmi tous les produits d'une commande)
    # Grouper par bon de commande pour obtenir les délais max par commande
    orders_data = supplier_data.groupby('Bon de commande').agg({
        'Délai théorique': 'max',
        'Délai réel': 'max',
        'Matériel': 'nunique',  # Nombre de produits uniques par commande
        'Date de comptabilisation': 'first',  # Date de la commande
        'Year': 'first',        # Année de la commande
        'Month': 'first'        # Mois de la commande
    }).reset_index()
    
    # Convertir les colonnes numériques en types appropriés
    orders_data['Bon de commande'] = orders_data['Bon de commande'].astype(str).str.replace('\.0$', '', regex=True)
    orders_data['Year'] = orders_data['Year'].astype(int)
    
    # Calculer la différence pour les commandes et arrondir à 1 décimale
    orders_data['Écart (jours)'] = (orders_data['Délai réel'] - orders_data['Délai théorique']).round(1)
    orders_data['Délai théorique'] = orders_data['Délai théorique'].round(1)
    orders_data['Délai réel'] = orders_data['Délai réel'].round(1)
    
    # Catégoriser les livraisons pour les commandes
    def categorize_delivery(row):
        if row['Écart (jours)'] < 0:
            return 'En avance'
        elif 0<= row['Écart (jours)'] <=1:
            return 'À temps'
        elif 2<= row['Écart (jours)'] <= 7:
            return 'Retard accepté'
        else:
            return 'Long délai'
    
    orders_data['Statut livraison'] = orders_data.apply(categorize_delivery, axis=1)
    
    # --- SECTION AJOUTÉE 1: Résumé par Année ---
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">Résumé des Commandes par Année</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Tableau 1: Nombre de commandes, produits uniques et produits commandés par année
    yearly_summary = supplier_data.groupby('Year').agg(
        Nombre_de_commandes=('Bon de commande', 'nunique'),
        Nombre_de_produits_uniques=('Matériel', 'nunique'),
        Nombre_total_de_produits=('Matériel', 'count')
    ).reset_index()
    
    yearly_summary.columns = ['Année', 'Nombre de commandes', 'Nombre de références', 'Nombre de lignes']
    
    # Convertir les années et les valeurs entières en format sans virgule
    yearly_summary['Année'] = yearly_summary['Année'].astype(int)
    yearly_summary['Nombre de commandes'] = yearly_summary['Nombre de commandes'].astype(int)
    yearly_summary['Nombre de références'] = yearly_summary['Nombre de références'].astype(int)
    yearly_summary['Nombre de lignes'] = yearly_summary['Nombre de lignes'].astype(int)
    
    # Créer un tableau stylisé
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h6 style="color: {color_palette['text']}; margin-top: 0;">Synthèse annuelle des volumes</h6>
    </div>
    """, unsafe_allow_html=True)
    
    # Appliquer des styles personnalisés pour le tableau - MODIFIÉ: couleurs différentes par colonne
    def color_yearly_summary(val, col_name):
        if isinstance(val, int):
            if col_name == 'Année':
                return f'background-color: {color_palette["quaternary"]}30;'
            elif col_name == 'Nombre de commandes':
                return f'background-color: {color_palette["primary"]}30;'
            elif col_name == 'Nombre de références':
                return f'background-color: {color_palette["secondary"]}30;'
            elif col_name == 'Nombre de lignes':
                return f'background-color: {color_palette["tertiary"]}30;'
        return ''
    
    # Appliquer les styles pour chaque colonne avec des couleurs différentes
    styled_yearly_summary = yearly_summary.style\
        .map(lambda x: color_yearly_summary(x, 'Année'), subset=['Année'])\
        .map(lambda x: color_yearly_summary(x, 'Nombre de commandes'), subset=['Nombre de commandes'])\
        .map(lambda x: color_yearly_summary(x, 'Nombre de références'), subset=['Nombre de produits uniques'])\
        .map(lambda x: color_yearly_summary(x, 'Nombre de lignes'), subset=['Nombre total de produits'])
    
    # Afficher le tableau sans l'index
    st.dataframe(styled_yearly_summary, use_container_width=True, hide_index=True)
    
    # --- SECTION AJOUTÉE 2: Délais moyens par Année ---
    st.markdown(f"""
    <div style="background-color:{color_palette['secondary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">Délais Moyens par Année</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculer les délais moyens par année pour les commandes
    yearly_order_delays = orders_data.groupby('Year').agg({
        'Délai théorique': 'mean',   # Délai théorique moyen par commande
        'Délai réel': 'mean',        # Délai réel moyen par commande
        'Écart (jours)': 'mean'      # Écart moyen par commande
    }).reset_index()
    
    yearly_order_delays.columns = ['Année', 'Délai théorique', 'Délai réel', 'Écart moyen']
    
    # Formater les nombres avec 1 décimale
    for col in yearly_order_delays.columns[1:]:
        yearly_order_delays[col] = yearly_order_delays[col].round(1)
    
    # Convertir les années en format sans virgule
    yearly_order_delays['Année'] = yearly_order_delays['Année'].astype(int)
    
    # Calculer les délais moyens par année pour les produits
    yearly_product_delays = supplier_data.groupby('Year').agg({
        'Délai théorique': 'mean',   # Délai théorique moyen par produit
        'Délai réel': 'mean'         # Délai réel moyen par produit
    }).reset_index()
    
    yearly_product_delays['Écart moyen'] = (yearly_product_delays['Délai réel'] - yearly_product_delays['Délai théorique']).round(1)
    
    yearly_product_delays.columns = ['Année', 'Délai théorique', 'Délai réel', 'Écart moyen']
    
    # Formater les nombres avec 1 décimale
    for col in yearly_product_delays.columns[1:]:
        yearly_product_delays[col] = yearly_product_delays[col].round(1)
    
    # Convertir les années en format sans virgule
    yearly_product_delays['Année'] = yearly_product_delays['Année'].astype(int)
    
    # Créer un tableau stylisé pour les délais - séparé en deux tableaux
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h6 style="color: {color_palette['text']}; margin-top: 0;">Délais moyens annuels par commande (en jours)</h6>
    </div>
    """, unsafe_allow_html=True)
    
    # Appliquer des styles personnalisés pour le tableau des commandes
    def color_delays(val, col_name):
        if isinstance(val, (int, float)):
            if col_name == 'Année':
                return f'background-color: {color_palette["quaternary"]}30;'
            elif col_name == 'Écart moyen' and val > 0:
                return f'background-color: {color_palette["negative"]}30;'
            elif col_name == 'Écart moyen' and val < 0:
                return f'background-color: {color_palette["positive"]}30;'
            elif col_name == 'Délai théorique':
                return f'background-color: {color_palette["secondary"]}30;'
            elif col_name == 'Délai réel':
                return f'background-color: {color_palette["tertiary"]}30;'
        return ''
    
    # Appliquer les styles pour le tableau des commandes
    styled_order_delays = yearly_order_delays.style\
        .map(lambda x: color_delays(x, 'Année'), subset=['Année'])\
        .map(lambda x: color_delays(x, 'Délai théorique'), subset=['Délai théorique'])\
        .map(lambda x: color_delays(x, 'Délai réel'), subset=['Délai réel'])\
        .map(lambda x: color_delays(x, 'Écart moyen'), subset=['Écart moyen'])\
        .format({
            'Délai théorique': '{:.1f}',
            'Délai réel': '{:.1f}',
            'Écart moyen': '{:.1f}'
        })
    
    # Afficher le tableau des commandes sans l'index
    st.dataframe(styled_order_delays, use_container_width=True, hide_index=True)
    
    # Créer un tableau stylisé pour les délais des produits
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h6 style="color: {color_palette['text']}; margin-top: 0;">Délais moyens annuels par produit (en jours)</h6>
    </div>
    """, unsafe_allow_html=True)
    
    # Appliquer les styles pour le tableau des produits
    styled_product_delays = yearly_product_delays.style\
        .map(lambda x: color_delays(x, 'Année'), subset=['Année'])\
        .map(lambda x: color_delays(x, 'Délai théorique'), subset=['Délai théorique'])\
        .map(lambda x: color_delays(x, 'Délai réel'), subset=['Délai réel'])\
        .map(lambda x: color_delays(x, 'Écart moyen'), subset=['Écart moyen'])\
        .format({
            'Délai théorique': '{:.1f}',
            'Délai réel': '{:.1f}',
            'Écart moyen': '{:.1f}'
        })
    
    # Afficher le tableau des produits sans l'index
    st.dataframe(styled_product_delays, use_container_width=True, hide_index=True)
    
 
    # --- SECTION AJOUTÉE 4: Produits toujours en retard ---
    st.markdown(f"""
    <div style="background-color:{color_palette['negative']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">Produits toujours en retard de livraison</h5>
    </div>
    """, unsafe_allow_html=True)

    # Identifier tous les produits uniques
    all_products = supplier_data[['Matériel', 'Description du matériel', 'Matériel du fournisseur']].drop_duplicates()

    # Initialiser un DataFrame pour stocker les produits toujours en retard
    always_delayed_products = []

    # Pour chaque produit, vérifier s'il est toujours en retard
    for _, product in all_products.iterrows():
        # Filtrer les données pour ce produit
        product_data = supplier_data[
            (supplier_data['Matériel'] == product['Matériel']) &
            (supplier_data['Description du matériel'] == product['Description du matériel']) &
            (supplier_data['Matériel du fournisseur'] == product['Matériel du fournisseur'])
        ]
        
        # Grouper par année et vérifier l'écart pour chaque année
        yearly_data = product_data.groupby('Year').agg({
            'Délai théorique': 'mean',
            'Délai réel': 'mean'
        })
        
        yearly_data['Écart'] = yearly_data['Délai réel'] - yearly_data['Délai théorique']
        
        # Vérifier si le produit est en retard pour toutes les années
        if (yearly_data['Écart'] > 0).all() and len(yearly_data) > 0:
            # Calculer le détail pour chaque année
            for year, row in yearly_data.iterrows():
                always_delayed_products.append({
                    'Matériel': product['Matériel'],
                    'Description du matériel': product['Description du matériel'],
                    'Matériel du fournisseur': product['Matériel du fournisseur'],
                    'Year': year,
                    'Délai théorique': row['Délai théorique'].round(1),
                    'Délai réel': row['Délai réel'].round(1),
                    'Écart annuel': row['Écart'].round(1)
                })

    # Convertir la liste en DataFrame
    if always_delayed_products:
        delayed_df = pd.DataFrame(always_delayed_products)
        
        # Calculer l'écart moyen global pour chaque produit
        avg_delay_by_product = delayed_df.groupby(['Matériel', 'Description du matériel', 'Matériel du fournisseur']).agg({
            'Écart annuel': 'mean',
            'Year': 'count'  # Nombre d'années où le produit a été commandé
        }).reset_index()
        
        # IMPORTANT: Gardons le même nom de colonne pour éviter l'erreur KeyError
        avg_delay_by_product.rename(columns={
            'Écart annuel': 'Écart moyen global',
            'Year': 'Nombre d\'années'
        }, inplace=True)
        
        avg_delay_by_product['Écart moyen global'] = avg_delay_by_product['Écart moyen global'].round(1)
        
        # Fusionner avec les données par année
        product_analysis = pd.merge(
            delayed_df,
            avg_delay_by_product,
            on=['Matériel', 'Description du matériel', 'Matériel du fournisseur'],
            how='left'
        )
        
        # Trier par écart moyen global décroissant
        product_analysis = product_analysis.sort_values('Écart moyen global', ascending=False)
        
        # Pivoter les données pour avoir les années en colonnes
        pivot_columns = ['Délai théorique', 'Délai réel', 'Écart annuel']
        final_table = pd.DataFrame()
        
        for column in pivot_columns:
            pivot_data = product_analysis.pivot_table(
                index=['Matériel', 'Description du matériel', 'Matériel du fournisseur', 'Écart moyen global', 'Nombre d\'années'],
                columns='Year',
                values=column,
                aggfunc='mean'
            ).reset_index()
            
            # Renommer les colonnes d'années
            year_columns = [col for col in pivot_data.columns if isinstance(col, int)]
            for year in year_columns:
                pivot_data.rename(columns={year: f'{column} {year}'}, inplace=True)
            
            if final_table.empty:
                final_table = pivot_data
            else:
                # Exclure les colonnes déjà dans final_table
                cols_to_use = [col for col in pivot_data.columns if col not in final_table.columns]
                final_table = pd.concat([final_table, pivot_data[cols_to_use]], axis=1)
        
        # Créer un tableau stylisé
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
            <h6 style="color: {color_palette['text']}; margin-top: 0;">Produits toujours en retard de livraison (ecart>0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Définir une fonction pour appliquer le dégradé à l'écart moyen global
        def color_ecart_progressif(val):
            if isinstance(val, (int, float)) and not pd.isna(val):
                if val > 0:
                    # Utiliser un dégradé plus sophistiqué pour l'écart
                    normalized_val = min(30, val) / 30
                    r = int(255 - (normalized_val * 50))
                    g = int(100 - (normalized_val * 70))
                    b = int(100 - (normalized_val * 70))
                    return f'background-color: rgb({r}, {g}, {b});'
                return ''
            return 'background-color: #FFB74D;'  # Orange pour None/NA
        
        # Fonction pour colorer toutes les cellules None en orange
        def color_none_cells(val):
            if pd.isna(val):
                return 'background-color: #FFB74D;'  # Orange pour None/NA
            return ''
        
        # Formatter les colonnes et appliquer les styles
        styled_final_table = final_table.style
        
        # Format pour nombre avec 1 décimale
        format_dict = {}
        for col in final_table.columns:
            if any(term in str(col) for term in ['Délai', 'Écart']):
                format_dict[col] = '{:.1f}'
        
        styled_final_table = styled_final_table.format(format_dict)
        
        # Définir des couleurs sophistiquées pour chaque type de colonne
        materiel_color = 'background-color: #1A237E40;'  # Bleu indigo profond avec transparence
        description_color = 'background-color: #0D47A140;'  # Bleu royal avec transparence
        fournisseur_color = 'background-color: #303F9F40;'  # Bleu indigo avec transparence
        delai_theorique_color = 'background-color: #00695C40;'  # Vert teal foncé avec transparence
        delai_reel_color = 'background-color: #00796B40;'  # Vert teal avec transparence
        ecart_annuel_color = 'background-color: #3E272340;'  # Marron foncé avec transparence
        nombre_annees_color = 'background-color: #5D403740;'  # Marron avec transparence
        
        # Appliquer des couleurs fixes à toutes les colonnes et gérer les None
        def style_all_columns(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            
            for col in df.columns:
                if col == 'Matériel':
                    styles[col] = materiel_color
                elif col == 'Description du matériel':
                    styles[col] = description_color
                elif col == 'Matériel du fournisseur':
                    styles[col] = fournisseur_color
                elif 'Délai théorique' in str(col):
                    styles[col] = delai_theorique_color
                elif 'Délai réel' in str(col):
                    styles[col] = delai_reel_color
                elif 'Écart annuel' in str(col):
                    styles[col] = ecart_annuel_color
                elif 'Nombre d\'années' in str(col):
                    styles[col] = nombre_annees_color
            
            return styles
        
        # Appliquer toutes les couleurs de base
        styled_final_table = styled_final_table.apply(style_all_columns, axis=None)
        
        # Appliquer le dégradé pour l'écart moyen global
        styled_final_table = styled_final_table.background_gradient(
            subset=['Écart moyen global'], 
            cmap="RdYlGn_r",
            vmin=0,
            vmax=final_table['Écart moyen global'].max()
        )
        
        # Colorer toutes les cellules None en orange
        for col in final_table.columns:
            styled_final_table = styled_final_table.map(
                lambda x: 'background-color: #FFB74D;' if pd.isna(x) else '', 
                subset=[col]
            )
        
        # Propriétés supplémentaires pour l'alignement et l'apparence
        styled_final_table = styled_final_table.set_properties(**{'text-align': 'center'})
        
        # Afficher le tableau sans l'index
        st.dataframe(styled_final_table, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucun produit n'a été systématiquement en retard chaque année.")

    # --- SECTION AJOUTÉE 3: Statut des livraisons par Année ---
    st.markdown(f"""
    <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">Statut des Livraisons par Année</h5>
    </div>
    """, unsafe_allow_html=True)

    # Pour les commandes - on utilise orders_data qui contient déjà les délais maximaux par commande
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h6 style="color: {color_palette['text']}; margin-top: 0;">Statuts de livraison par année (par commande)</h6>
    </div>
    """, unsafe_allow_html=True)

    # Vérifier si la colonne 'Statut livraison' existe déjà dans orders_data, sinon la calculer
    if 'Statut livraison' not in orders_data.columns:
        # La fonction categorize_delivery est déjà définie plus haut dans le code
        orders_data['Statut livraison'] = orders_data.apply(categorize_delivery, axis=1)

    # Compter le nombre total de commandes par année
    total_orders_by_year = orders_data.groupby('Year').size()

    # Compter le nombre de commandes par année et par statut
    orders_status_count = orders_data.groupby(['Year', 'Statut livraison']).size().unstack(fill_value=0)

    # S'assurer que toutes les colonnes de statut existent
    for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
        if status not in orders_status_count.columns:
            orders_status_count[status] = 0

    # Calculer les pourcentages
    order_status_by_year = orders_status_count.copy()
    for col in order_status_by_year.columns:
        order_status_by_year[col] = (orders_status_count[col] / total_orders_by_year * 100).round(1)

    # Réinitialiser l'index pour avoir Year comme colonne
    order_status_display = order_status_by_year.reset_index()
    order_status_display['Year'] = order_status_display['Year'].astype(int)

    # Renommer la colonne 'Year' en 'Année'
    order_status_display = order_status_display.rename(columns={'Year': 'Année'})

    # Définir les couleurs pour chaque statut
    status_colors = {
        'En avance': color_palette["positive"],
        'À temps': color_palette["neutral"],
        'Retard accepté': color_palette["quaternary"],
        'Long délai': color_palette["negative"]
    }

    # Fonction pour colorer les cellules
    def color_cells(val, col_name):
        if col_name == 'Année':
            return f'background-color: {color_palette["quaternary"]}30;'
        for status, color in status_colors.items():
            if col_name == status:
                return f'background-color: {color}30;'
        return ''

    # Appliquer les styles pour chaque colonne
    styled_order_status = order_status_display.style
    for col in order_status_display.columns:
        styled_order_status = styled_order_status.map(
            lambda x: color_cells(x, col), 
            subset=[col]
        )

    # Formater pour afficher avec un signe de pourcentage
    format_dict = {col: '{:.1f}%' for col in order_status_display.columns if col != 'Année'}
    styled_order_status = styled_order_status.format(format_dict)

    # Afficher le tableau des statuts de commande sans l'index
    st.dataframe(styled_order_status, use_container_width=True, hide_index=True)

    # Pour les produits individuels
    st.markdown(f"""
    <div style="background-color:{color_palette['background']}; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h6 style="color: {color_palette['text']}; margin-top: 0;">Statuts de livraison par année (par produit)</h6>
    </div>
    """, unsafe_allow_html=True)

    # Calculer l'écart et le statut pour chaque produit s'ils n'existent pas déjà
    if 'Écart (jours)' not in supplier_data.columns:
        supplier_data['Écart (jours)'] = (supplier_data['Délai réel'] - supplier_data['Délai théorique']).round(1)

    if 'Statut livraison' not in supplier_data.columns:
        supplier_data['Statut livraison'] = supplier_data.apply(categorize_delivery, axis=1)

    # Compter le nombre total de produits par année
    total_products_by_year = supplier_data.groupby('Year').size()

    # Compter le nombre de produits par année et par statut
    products_status_count = supplier_data.groupby(['Year', 'Statut livraison']).size().unstack(fill_value=0)

    # S'assurer que toutes les colonnes de statut existent
    for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
        if status not in products_status_count.columns:
            products_status_count[status] = 0

    # Calculer les pourcentages
    product_status_by_year = products_status_count.copy()
    for col in product_status_by_year.columns:
        product_status_by_year[col] = (products_status_count[col] / total_products_by_year * 100).round(1)

    # Réinitialiser l'index pour avoir Year comme colonne
    product_status_display = product_status_by_year.reset_index()
    product_status_display['Year'] = product_status_display['Year'].astype(int)

    # Renommer la colonne 'Year' en 'Année'
    product_status_display = product_status_display.rename(columns={'Year': 'Année'})

    # Appliquer les styles pour chaque colonne
    styled_product_status = product_status_display.style
    for col in product_status_display.columns:
        styled_product_status = styled_product_status.map(
            lambda x: color_cells(x, col), 
            subset=[col]
        )

    # Formater pour afficher avec un signe de pourcentage
    format_dict = {col: '{:.1f}%' for col in product_status_display.columns if col != 'Année'}
    styled_product_status = styled_product_status.format(format_dict)

    # Afficher le tableau des statuts de produit sans l'index
    st.dataframe(styled_product_status, use_container_width=True, hide_index=True)
