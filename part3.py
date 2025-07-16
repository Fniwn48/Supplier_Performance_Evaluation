import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import locale; locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8' if 'win' not in __import__('sys').platform else 'French_France.1252')
from datetime import datetime

def part_three(df, year, month, vendor_search):
    """
    Analyse des performances d'un fournisseur spécifique pour une année et un mois donnés
    
    Args:
        df: DataFrame contenant les données complètes
        year: Année sélectionnée
        month: Mois sélectionné
        vendor_search: Nom ou ID du fournisseur à analyser
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
    
    # Palette pour les statuts de livraison
    delivery_status_colors = {
        'En avance': color_palette['positive'], 
        'À temps': color_palette['neutral'], 
        'Retard accepté': color_palette['quaternary'],  # Ambre pour retard accepté
        'Long délai': color_palette['negative']  # Rouge pour long délai
    }

    # Filtrer les données pour le fournisseur sélectionné
    supplier_data = df[(df['Nom du fournisseur'] == vendor_search) | 
                     (df['Fournisseur'] == vendor_search)].copy()
    
    if supplier_data.empty:
        st.warning(f"Aucune donnée disponible pour le fournisseur {vendor_search}")
        return
    
    # Récupérer le nom et l'ID du fournisseur
    supplier_name = supplier_data['Nom du fournisseur'].iloc[0]
    supplier_id = supplier_data['Fournisseur'].iloc[0].astype(int)
    
    # Filtrer par année et mois
    mask_current = (supplier_data['Year'] == year) & (supplier_data['Month'] == month)
    current_data = supplier_data[mask_current].copy()
    
    if current_data.empty:
        month_name = datetime(2022, month, 1).strftime('%B')
        st.warning(f"Aucune donnée disponible pour {supplier_name} en {month_name} {year}")
        return
    
    # Déterminer le mois précédent
    prev_month = month
    prev_year = year - 1
    
    
    # Filtrer les données pour le mois précédent
    mask_prev = (supplier_data['Year'] == prev_year) & (supplier_data['Month'] == prev_month)
    prev_data = supplier_data[mask_prev].copy()
    
    # Obtenir les noms des mois
    current_month_name = datetime(2022, month, 1).strftime('%B')
    prev_month_name = datetime(2022, month, 1).strftime('%B')
    
    # Utiliser un style personnalisé pour l'en-tête
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 10px; border-radius: 10px;">
        <h4 style="color: white; text-align: center;">Analyse du fournisseur: {supplier_name} (ID: {supplier_id})</h4>
        <h5 style="color: white; text-align: center;">{current_month_name} {year}</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculer les délais pour les commandes (le délai le plus long parmi tous les produits d'une commande)
    # Grouper par bon de commande pour obtenir les délais max par commande
    current_orders = current_data.groupby('Bon de commande').agg({
        'Délai théorique': 'max',
        'Délai réel': 'max',
        'Matériel': 'nunique',  # Nombre de produits uniques par commande
        'Date de comptabilisation': 'first',  # Date de la commande
    }).reset_index()
    
    # Faire la même chose pour le mois précédent
    if not prev_data.empty:
        prev_orders = prev_data.groupby('Bon de commande').agg({
            'Délai théorique': 'max',
            'Délai réel': 'max',
            'Matériel': 'nunique',  # Nombre de produits uniques par commande
            'Date de comptabilisation': 'first',  # Date de la commande
        }).reset_index()
    else:
        prev_orders = pd.DataFrame()
    
    # Convertir les colonnes numériques en types appropriés
    current_orders['Bon de commande'] = current_orders['Bon de commande'].astype(str).str.replace('\.0$', '', regex=True)
    
    # Calculer la différence pour les commandes et arrondir à 1 décimale
    current_orders['Délai théorique'] = current_orders['Délai théorique'].round(1)
    current_orders['Délai réel'] = current_orders['Délai réel'].round(1)
    current_orders['Écart_commande (jours)'] = (current_orders['Délai réel'] - current_orders['Délai théorique']).round(1)
    
    
    # Catégoriser les livraisons pour les commandes
    def categorize_delay(row):
        days_diff = row['Écart_commande (jours)'] if 'Écart_commande (jours)' in row.index else row['Écart de délai']
        if days_diff < 0:
            return "En avance"
        elif 0 <= days_diff <= 1:
            return "À temps"
        elif 2 <= days_diff <= 7:
            return "Retard accepté"
        else:  # 8 days or more
            return "Long délai"
    
    current_orders['Statut livraison'] = current_orders.apply(categorize_delay, axis=1)
    
    # S'assurer que les colonnes Écart existent et sont correctement calculées
    if 'Écart de délai' not in current_data.columns:
        current_data['Écart de délai'] = (current_data['Délai réel'] - current_data['Délai théorique']).round(1)
    
    # Arrondir à 1 décimale
    current_data['Délai théorique'] = current_data['Délai théorique'].round(1)
    current_data['Délai réel'] = current_data['Délai réel'].round(1)
    current_data['Écart (jours)'] = current_data['Écart de délai'].round(1)
    
    # Ajouter la catégorisation pour les produits
    current_data['Statut de livraison'] = current_data.apply(categorize_delay, axis=1)
    
    # --- SECTION 1: INDICATEURS CLÉS ---
    st.markdown(f"""
    <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center; margin: 0;">KPIS</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcul des indicateurs clés
    total_orders = len(current_orders)
    total_products = current_data['Matériel'].nunique()
    total_products_count = len(current_data)
    
    # Calcul des délais moyens pour les commandes
    order_delay_means = {
        'Théorique': current_orders['Délai théorique'].mean().round(1),
        'Réel': current_orders['Délai réel'].mean().round(1),
        'Écart': current_orders['Écart_commande (jours)'].mean().round(1)
    }
    
    # Calcul des délais moyens pour les produits
    product_delay_means = {
        'Théorique': current_data['Délai théorique'].mean().round(1),
        'Réel': current_data['Délai réel'].mean().round(1),
        'Écart': current_data['Écart de délai'].mean().round(1)
    }
    
    # Affichage des indicateurs clés en 3 colonnes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="color:{color_palette['primary']}; margin:0;">{total_orders}</h4>
            <p style="margin:5px 0 0 0;">Nombre de commandes</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="color:{color_palette['primary']}; margin:0;">{total_products}</h4>
            <p style="margin:5px 0 0 0;">Nombre de références</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding:20px; border-radius:10px; text-align:center;">
            <h4 style="color:{color_palette['primary']}; margin:0;">{total_products_count}</h4>
            <p style="margin:5px 0 0 0;">Nombre de lignes</p>
        </div>
        """, unsafe_allow_html=True)
    
    # --- SECTION 2: DÉLAIS MOYENS (GRAPHIQUES EN CERCLE) ---
    st.markdown(f"""
    <div style="background-color:{color_palette['secondary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center;margin: 0;">Délais Moyens</h5>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Préparation des données pour le graphique circulaire des commandes
        order_data = pd.DataFrame({
            'Délai': ['Théorique', 'Réel'],
            'Jours': [order_delay_means['Théorique'], order_delay_means['Réel']]
        })
        
        # Création du graphique circulaire pour les commandes
        fig_order = px.pie(
            order_data,
            names='Délai',
            values='Jours',
            title=f"Délais moyens par commande",
            color='Délai',
            color_discrete_map={
                'Théorique': color_palette['neutral'],
                'Réel': color_palette['tertiary'],
                'Écart': color_palette['negative'] if order_delay_means['Écart'] > 0 else color_palette['positive']
            },
            hole=0.4
        )
        
        fig_order.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_order.update_layout(
            title_font_size=16,
            title_font_color=color_palette['text'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend_title_text='Type de délai',
            annotations=[dict(text=f"{order_delay_means['Écart']:+.1f}j", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig_order, use_container_width=True)
        
        # Afficher les valeurs exactes sous le graphique
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; text-align: center;">
            <p style="margin: 0;">Délai théorique: <b>{order_delay_means['Théorique']} jours</b></p>
            <p style="margin: 0;">Délai réel: <b>{order_delay_means['Réel']} jours</b></p>
            <p style="margin: 0;">Écart: <b style="color: {color_palette['negative'] if order_delay_means['Écart'] > 0 else color_palette['positive']};">{order_delay_means['Écart']:+.1f} jours</b></p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        # Préparation des données pour le graphique circulaire des produits
        product_data = pd.DataFrame({
            'Délai': ['Théorique', 'Réel'],
            'Jours': [product_delay_means['Théorique'], product_delay_means['Réel']]
        })
        
        # Création du graphique circulaire pour les produits
        fig_product = px.pie(
            product_data,
            names='Délai',
            values='Jours',
            title=f"Délais moyens par produit",
            color='Délai',
            color_discrete_map={
                'Théorique': color_palette['neutral'],
                'Réel': color_palette['tertiary'],
                'Écart': color_palette['negative'] if product_delay_means['Écart'] > 0 else color_palette['positive']
            },
            hole=0.4
        )
        
        fig_product.update_traces(textposition='inside', textinfo='percent+label+value')
        fig_product.update_layout(
            title_font_size=16,
            title_font_color=color_palette['text'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend_title_text='Type de délai',
            annotations=[dict(text=f"{product_delay_means['Écart']:+.1f}j", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        st.plotly_chart(fig_product, use_container_width=True)
        
        # Afficher les valeurs exactes sous le graphique
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; text-align: center;">
            <p style="margin: 0;">Délai théorique: <b>{product_delay_means['Théorique']} jours</b></p>
            <p style="margin: 0;">Délai réel: <b>{product_delay_means['Réel']} jours</b></p>
            <p style="margin: 0;">Écart: <b style="color: {color_palette['negative'] if product_delay_means['Écart'] > 0 else color_palette['positive']};">{product_delay_means['Écart']:+.1f} jours</b></p>
        </div>
        """, unsafe_allow_html=True)

    # --- SECTION 3: COMPARAISON AVEC LE MOIS  ---
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white; text-align: center; margin: 0;">Comparaison avec le Mois {current_month_name} de {prev_year} </h5>
    </div>
    """, unsafe_allow_html=True)

    if not prev_data.empty:
        # Calcul des indicateurs clés pour le mois précédent
        prev_total_orders = len(prev_orders)
        prev_total_products = prev_data['Matériel'].nunique()
        prev_total_products_count = len(prev_data)
        
        # Calcul de l'évolution (pourcentage)
        order_change = round(((total_orders - prev_total_orders) / prev_total_orders * 100), 1) if prev_total_orders > 0 else 100
        product_change = round(((total_products - prev_total_products) / prev_total_products * 100), 1) if prev_total_products > 0 else 100
        product_count_change = round(((total_products_count - prev_total_products_count) / prev_total_products_count * 100), 1) if prev_total_products_count > 0 else 100
        
        # Affichage des évolutions en 3 colonnes
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-top: 15px;">
            <h4 style="color:{color_palette['text']};">Évolution des volumes par rapport à {prev_month_name} {prev_year}:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            change_color = color_palette['positive'] if order_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Commandes: {prev_total_orders} → {total_orders}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{order_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            change_color = color_palette['positive'] if product_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Produits uniques: {prev_total_products} → {total_products}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{product_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            change_color = color_palette['positive'] if product_count_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Total produits commandés: {prev_total_products_count} → {total_products_count}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{product_count_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
        
        # Calcul des délais moyens pour les commandes du mois précédent
        if not prev_orders.empty:
            prev_orders['Écart_commande (jours)'] = (prev_orders['Délai réel'] - prev_orders['Délai théorique']).round(1)
            
            prev_order_delay_means = {
                'Théorique': prev_orders['Délai théorique'].mean().round(1),
                'Réel': prev_orders['Délai réel'].mean().round(1),
                'Écart': prev_orders['Écart_commande (jours)'].mean().round(1)
            }
            
            # Calcul des délais moyens pour les produits du mois précédent
            prev_data['Écart de délai'] = (prev_data['Délai réel'] - prev_data['Délai théorique']).round(1)
            
            prev_product_delay_means = {
                'Théorique': prev_data['Délai théorique'].mean().round(1),
                'Réel': prev_data['Délai réel'].mean().round(1),
                'Écart': prev_data['Écart de délai'].mean().round(1)
            }
            
            # Évolution des délais
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-top: 15px;">
                <h4 style="color:{color_palette['text']};">Évolution des délais par rapport à {prev_month_name} {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)

            # Création de tableaux pour l'évolution des délais
            tab1, tab2 = st.tabs(["Délais par commande", "Délais par produit"])

            # Onglet Délais par commande
            with tab1:
                # Préparation des données pour le tableau d'évolution des commandes
                order_evolution = pd.DataFrame({
                    'Type': ['Théorique', 'Réel', 'Écart'],
                    f'Actuel ({current_month_name})': [
                        round(order_delay_means['Théorique'], 1), 
                        round(order_delay_means['Réel'], 1), 
                        round(order_delay_means['Écart'], 1)
                    ],
                    f'Précédent ({prev_month_name})': [
                        round(prev_order_delay_means['Théorique'], 1), 
                        round(prev_order_delay_means['Réel'], 1), 
                        round(prev_order_delay_means['Écart'], 1)
                    ],
                    'Évolution (jours)': [
                        round(order_delay_means['Théorique'] - prev_order_delay_means['Théorique'], 1),
                        round(order_delay_means['Réel'] - prev_order_delay_means['Réel'], 1),
                        round(order_delay_means['Écart'] - prev_order_delay_means['Écart'], 1)
                    ]
                })
                
                # Fonction pour styliser l'évolution
                def highlight_evolution(val):
                    if isinstance(val, (int, float)):
                        if val < 0:
                            # Pour l'écart, négatif est mieux (donc vert)
                            return f'background-color: {color_palette["positive"]}; color: white'
                        elif val > 0:
                            # Pour l'écart, positif est pire (donc rouge)
                            return f'background-color: {color_palette["negative"]}; color: white'
                    return ''
                
                # Fonction pour colorer les colonnes (comme dans l'exemple part1_one)
                def highlight_columns_order(x):
                    df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
                    df_styler['Type'] = 'background-color: #f5f5f5'
                    df_styler[f'Actuel ({current_month_name})'] = f'background-color: {color_palette["primary"]}; color: white'
                    df_styler[f'Précédent ({prev_month_name})'] = f'background-color: {color_palette["secondary"]}; color: white'
                    df_styler['Évolution (jours)'] = 'background-color: #e1f5fe'
                    return df_styler
                
                # Appliquer le style au DataFrame
                styled_order_evolution = order_evolution.style.apply(
                    highlight_columns_order, axis=None
                ).applymap(
                    highlight_evolution, subset=['Évolution (jours)']
                ).format({
                    f'Actuel ({current_month_name})': '{:.1f}',
                    f'Précédent ({prev_month_name})': '{:.1f}',
                    'Évolution (jours)': '{:.1f}'
                })
                
                # Afficher le tableau
                st.dataframe(styled_order_evolution, use_container_width=True, hide_index=True)

            # Onglet Délais par produit
            with tab2:
                # Préparation des données pour le tableau d'évolution des produits
                product_evolution = pd.DataFrame({
                    'Type': ['Théorique', 'Réel', 'Écart'],
                    f'Actuel ({current_month_name})': [
                        round(product_delay_means['Théorique'], 1), 
                        round(product_delay_means['Réel'], 1), 
                        round(product_delay_means['Écart'], 1)
                    ],
                    f'Précédent ({prev_month_name})': [
                        round(prev_product_delay_means['Théorique'], 1), 
                        round(prev_product_delay_means['Réel'], 1), 
                        round(prev_product_delay_means['Écart'], 1)
                    ],
                    'Évolution (jours)': [
                        round(product_delay_means['Théorique'] - prev_product_delay_means['Théorique'], 1),
                        round(product_delay_means['Réel'] - prev_product_delay_means['Réel'], 1),
                        round(product_delay_means['Écart'] - prev_product_delay_means['Écart'], 1)
                    ]
                })
                
                # Appliquer le style au DataFrame
                styled_product_evolution = product_evolution.style.apply(
                    highlight_columns_order, axis=None
                ).applymap(
                    highlight_evolution, subset=['Évolution (jours)']
                ).format({
                    f'Actuel ({current_month_name})': '{:.1f}',
                    f'Précédent ({prev_month_name})': '{:.1f}',
                    'Évolution (jours)': '{:.1f}'
                })
                
                # Afficher le tableau
                st.dataframe(styled_product_evolution, use_container_width=True, hide_index=True)

    else:
        st.info(f"Aucune donnée disponible pour {prev_month_name} {prev_year} pour comparaison")



    # --- SECTION 4: RÉPARTITION DES STATUTS DE LIVRAISON ---
    st.markdown(f"""
    <div style="background-color:{color_palette['quaternary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white; text-align: center;margin: 0;">Répartition des Statuts de Livraison</h5>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculer les pourcentages actuels
    status_counts = current_orders['Statut livraison'].value_counts().reset_index()
    status_counts.columns = ['Statut livraison', 'count']
    total_orders = len(current_orders)
    status_counts['percentage'] = (status_counts['count'] / total_orders * 100).round(1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique circulaire pour les pourcentages actuels
        fig_pie = px.pie(
            status_counts,
            names='Statut livraison',
            values='count',
            color='Statut livraison',
            color_discrete_map=delivery_status_colors,
            title=f"Répartition des commandes en {current_month_name} {year}",
            labels={'Statut livraison': 'Statut de livraison', 'count': 'Nombre de commandes'},
            hole=0.4
        )
        
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            title_font_size=16,
            title_font_color=color_palette['text'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Comparaison avec le mois précédent si des données sont disponibles
        if not prev_orders.empty:
            prev_orders['Statut livraison'] = prev_orders.apply(categorize_delay, axis=1)
            prev_status_counts = prev_orders['Statut livraison'].value_counts().reset_index()
            prev_status_counts.columns = ['Statut livraison', 'count']
            prev_total_orders = len(prev_orders)
            prev_status_counts['percentage'] = (prev_status_counts['count'] / prev_total_orders * 100).round(1)
            
            # Préparation des données de comparaison           
            
            comparison_data = []

            # Créons des dictionnaires pour faciliter l'accès aux pourcentages
            current_pct_dict = dict(zip(status_counts['Statut livraison'], status_counts['percentage']))
            prev_pct_dict = dict(zip(prev_status_counts['Statut livraison'], prev_status_counts['percentage']))

            for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
                # Obtenez les pourcentages de manière plus fiable
                current_pct = current_pct_dict.get(status, 0)
                prev_pct = prev_pct_dict.get(status, 0)
                evolution = current_pct - prev_pct
                
                # Déterminer la couleur de l'évolution
                if status == 'Retard accepté' or status == 'Long délai':
                    evolution_color = color_palette['negative'] if evolution > 0 else color_palette['positive']
                else:
                    evolution_color = color_palette['positive'] if evolution > 0 else color_palette['negative']
                
                comparison_data.append({
                    'Statut': status,
                    f'% {prev_month_name}': f"{prev_pct:.1f}%",
                    'Évolution': f"{evolution:+.1f}%",
                    'color': evolution_color
                })
                        
            comparison_df = pd.DataFrame(comparison_data)
            
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
                <h4 style="color:{color_palette['text']};">Comparaison avec {prev_month_name} {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher le tableau avec des couleurs personnalisées
            for i, row in comparison_df.iterrows():
                col1, col2, col3 = st.columns([2.5, 1.5, 1.5])
                with col1:
                    st.markdown(f"<div style='font-weight:bold;'>{row['Statut']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"{row[f'% {prev_month_name}']}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div style='color:{row['color']};font-weight:bold;'>{row['Évolution']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Aucune donnée disponible pour {prev_month_name} {prev_year}")

   

    st.markdown("""<hr style="width:30%; margin:auto; border:1px solid gray;">""",unsafe_allow_html=True)

    # Calculer les pourcentages actuels pour les produits
    current_data['Statut de livraison'] = current_data.apply(categorize_delay, axis=1)
    status_counts_products = current_data['Statut de livraison'].value_counts().reset_index()
    status_counts_products.columns = ['Statut de livraison', 'count']
    total_products_count = len(current_data)
    status_counts_products['percentage'] = (status_counts_products['count'] / total_products_count * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        # Graphique circulaire pour les pourcentages actuels des produits
        fig_pie_products = px.pie(
            status_counts_products,
            names='Statut de livraison',
            values='count',
            color='Statut de livraison',
            color_discrete_map=delivery_status_colors,
            title=f"Répartition des produits en {current_month_name} {year}",
            labels={'Statut de livraison': 'Statut de livraison', 'count': 'Nombre de produits'},
            hole=0.4
        )
        
        fig_pie_products.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie_products.update_layout(
            title_font_size=16,
            title_font_color=color_palette['text'],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie_products, use_container_width=True)

    with col2:
        # Comparaison avec le mois précédent si des données sont disponibles
        if not prev_data.empty:
            prev_data['Statut de livraison'] = prev_data.apply(categorize_delay, axis=1)
            prev_status_counts_products = prev_data['Statut de livraison'].value_counts().reset_index()
            prev_status_counts_products.columns = ['Statut de livraison', 'count']
            prev_total_products_count = len(prev_data)
            prev_status_counts_products['percentage'] = (prev_status_counts_products['count'] / prev_total_products_count * 100).round(1)
            
            # Préparation des données de comparaison
            comparison_data_products = []

            # Créons des dictionnaires pour faciliter l'accès aux pourcentages
            current_pct_dict = dict(zip(status_counts_products['Statut de livraison'], status_counts_products['percentage']))
            prev_pct_dict = dict(zip(prev_status_counts_products['Statut de livraison'], prev_status_counts_products['percentage']))

            for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
                # Obtenez les pourcentages de manière plus fiable
                current_pct = current_pct_dict.get(status, 0)
                prev_pct = prev_pct_dict.get(status, 0)
                evolution = current_pct - prev_pct
                
                # Déterminer la couleur de l'évolution
                if status == 'Retard accepté' or status == 'Long délai':
                    evolution_color = color_palette['negative'] if evolution > 0 else color_palette['positive']
                else:
                    evolution_color = color_palette['positive'] if evolution > 0 else color_palette['negative']
                
                comparison_data_products.append({
                    'Statut': status,
                    f'% {prev_month_name}': f"{prev_pct:.1f}%",
                    'Évolution': f"{evolution:+.1f}%",
                    'color': evolution_color
                })
            
            comparison_df_products = pd.DataFrame(comparison_data_products)
            
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
                <h4 style="color:{color_palette['text']};">Comparaison avec {prev_month_name} {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher le tableau avec des couleurs personnalisées
            for i, row in comparison_df_products.iterrows():
                col1, col2, col3 = st.columns([2.5, 1.5, 1.5])
                with col1:
                    st.markdown(f"<div style='font-weight:bold;'>{row['Statut']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"{row[f'% {prev_month_name}']}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div style='color:{row['color']};font-weight:bold;'>{row['Évolution']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Aucune donnée disponible pour {prev_month_name} {prev_year}")
    
    # --- SECTION : TOP ET PIRES COMMANDES PAR ÉCART ---
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center;margin: 0;">Analyse des Commandes</h5>
    </div>
    """, unsafe_allow_html=True)

    # Séparation des commandes en bonnes et mauvaises
    good_orders = current_orders[current_orders['Écart_commande (jours)'] <= 0].sort_values('Écart_commande (jours)').copy()
    bad_orders = current_orders[current_orders['Écart_commande (jours)'] > 0].sort_values('Écart_commande (jours)', ascending=False).copy()

    # Obtenir des informations supplémentaires sur les commandes
    def enrich_order_data(order_df, supplier_df):
        # Copier les DataFrames pour éviter de modifier les originaux
        enriched = order_df.copy()
        supplier_copy = supplier_df.copy()
        
        # Convertir 'Bon de commande' en string dans les deux DataFrames
        # et nettoyer les valeurs pour assurer la compatibilité
        enriched['Bon de commande'] = enriched['Bon de commande'].astype(str).str.strip()
        supplier_copy['Bon de commande'] = supplier_copy['Bon de commande'].astype(str).str.strip()
        
        # Remplacer les chaînes vides par NaN
        enriched['Bon de commande'] = enriched['Bon de commande'].replace('', float('nan'))
        supplier_copy['Bon de commande'] = supplier_copy['Bon de commande'].replace('', float('nan'))
        
        # Effectuer la fusion en utilisant une méthode plus robuste
        # Imprimer des informations de diagnostic
        print(f"Shape avant fusion: {enriched.shape}")
        print(f"Types avant fusion: {enriched['Bon de commande'].dtype}")
        print(f"Exemple de 'Bon de commande' dans enriched: {enriched['Bon de commande'].iloc[0] if len(enriched) > 0 else 'vide'}")
        
        # Arrondir les valeurs numériques
        for col in ['Délai théorique', 'Délai réel', 'Écart_commande (jours)']:
            if col in enriched.columns:
                enriched[col] = enriched[col].round(1)
        
        return enriched

    # Enrichir les données des bonnes et mauvaises commandes
    good_orders = enrich_order_data(good_orders, current_data)
    bad_orders = enrich_order_data(bad_orders, current_data)

    # Colonnes à afficher
    order_display_cols = [
        'Bon de commande', 'Délai théorique', 'Délai réel', 'Écart_commande (jours)', 'Statut livraison'
    ]


    order_tabs = st.tabs(["📈 Meilleurs Commandes (Écart ≤ 0)", "📉 Mauvaises Commandes (Écart > 0)"])

    with order_tabs[0]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['positive']}; margin: 0;">Meilleurs commandes (Écart ≤ 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Formater les données pour l'affichage
        display_good_orders = good_orders[order_display_cols].copy()
        
        # S'assurer que les délais sont affichés avec un seul chiffre après la virgule
        for col in ['Délai théorique', 'Délai réel', 'Écart_commande (jours)']:
            if col in display_good_orders.columns:
                display_good_orders[col] = display_good_orders[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else x)
        
        # S'assurer que les numéros de commande sont des entiers sans décimales
        if 'Bon de commande' in display_good_orders.columns and display_good_orders['Bon de commande'].dtype != 'object':
            display_good_orders['Bon de commande'] = display_good_orders['Bon de commande'].astype(int)
        
        # Styliser le dataframe en combinant les couleurs par colonne et le gradient pour Écart
        if not display_good_orders.empty:
            styled_good_orders = display_good_orders.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Bon de commande' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["positive"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart_commande (jours)' else
                f'background-color: {color_palette["positive" if x["Statut livraison"] == "En avance" else "neutral" if x["Statut livraison"] == "À temps" else "negative"]}30; font-weight: bold; color: {color_palette["text"]}'
                for col in display_good_orders.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart
            numeric_good_orders = good_orders[order_display_cols].copy()
            styled_good_orders = styled_good_orders.background_gradient(
                subset=['Écart_commande (jours)'], 
                cmap="RdYlGn_r",
                vmin=numeric_good_orders['Écart_commande (jours)'].min(),
                vmax=0
            )
            
            st.dataframe(styled_good_orders, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune commande avec un écart favorable trouvée dans cette période.")

    with order_tabs[1]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['negative']}; margin: 0;">Commandes à améliorer (Écart > 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Formater les données pour l'affichage
        display_bad_orders = bad_orders[order_display_cols].copy()
        
        # S'assurer que les délais sont affichés avec un seul chiffre après la virgule
        for col in ['Délai théorique', 'Délai réel', 'Écart_commande (jours)']:
            if col in display_bad_orders.columns:
                display_bad_orders[col] = display_bad_orders[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else x)
        
        # S'assurer que les numéros de commande sont des entiers sans décimales
        if 'Bon de commande' in display_bad_orders.columns and display_bad_orders['Bon de commande'].dtype != 'object':
            display_bad_orders['Bon de commande'] = display_bad_orders['Bon de commande'].astype(int)
        
        # Styliser le dataframe en combinant les couleurs par colonne et le gradient pour Écart
        if not display_bad_orders.empty:
            styled_bad_orders = display_bad_orders.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Bon de commande' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["negative"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart_commande (jours)' else
                f'background-color: {color_palette["positive" if x["Statut livraison"] == "En avance" else "neutral" if x["Statut livraison"] == "À temps" else "negative"]}30; font-weight: bold; color: {color_palette["text"]}'
                for col in display_bad_orders.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart
            numeric_bad_orders = bad_orders[order_display_cols].copy()
            styled_bad_orders = styled_bad_orders.background_gradient(
                subset=['Écart_commande (jours)'], 
                cmap="RdYlGn_r",
                vmin=0,
                vmax=numeric_bad_orders['Écart_commande (jours)'].max()
            )
            
            st.dataframe(styled_bad_orders, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune commande avec un écart défavorable trouvée dans cette période.")


    # --- SECTION 6: TOP ET PIRES PRODUITS PAR ÉCART ---

    st.markdown(f"""
    <div style="background-color:{color_palette['secondary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center;margin: 0;">Analyse des Produits</h5>
    </div>
    """, unsafe_allow_html=True)

    # Séparation des produits en bons et mauvais
    good_products = current_data[current_data['Écart de délai'] <= 0].sort_values('Écart de délai').copy()
    bad_products = current_data[current_data['Écart de délai'] > 0].sort_values('Écart de délai', ascending=False).copy()

    # S'assurer que les délais ont un seul chiffre après la virgule
    for df in [good_products, bad_products]:
        for col in ['Délai théorique', 'Délai réel', 'Écart de délai']:
            if col in df.columns:
                df[col] = df[col].round(1)
        
        # S'assurer que les numéros de commande sont des entiers sans décimales
        if 'Bon de commande' in df.columns and df['Bon de commande'].dtype != 'object':
            df['Bon de commande'] = df['Bon de commande'].astype(int)

    # Colonnes à afficher pour les produits
    product_display_cols = [
        'Matériel', 'Description du matériel', 'Bon de commande', 
        'Délai théorique', 'Délai réel', 'Écart de délai', 'Statut de livraison'
    ]


    product_tabs = st.tabs(["📈 Produits Performants (Écart ≤ 0)", "📉 Produits à Améliorer (Écart > 0)"])

    with product_tabs[0]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['positive']}; margin: 0;">Meilleurs Produits (Écart ≤ 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Formater les données pour l'affichage
        display_good_products = good_products[product_display_cols].copy()
        
        # S'assurer que les délais sont affichés avec un seul chiffre après la virgule
        for col in ['Délai théorique', 'Délai réel', 'Écart de délai']:
            if col in display_good_products.columns:
                display_good_products[col] = display_good_products[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else x)
        
        # S'assurer que les numéros de commande sont des entiers sans décimales
        if 'Bon de commande' in display_good_products.columns and display_good_products['Bon de commande'].dtype != 'object':
            display_good_products['Bon de commande'] = display_good_products['Bon de commande'].astype(int)
        
        # Styliser le dataframe en combinant les couleurs par colonne et le gradient pour Écart
        if not display_good_products.empty:
            styled_good_products = display_good_products.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Description du matériel' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == 'Bon de commande' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["positive"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart de délai' else
                f'background-color: {color_palette["positive" if x["Statut de livraison"] == "En avance" else "neutral" if x["Statut de livraison"] == "À temps" else "negative"]}30; font-weight: bold; color: {color_palette["text"]}'
                for col in display_good_products.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart
            numeric_good_products = good_products[product_display_cols].copy()
            styled_good_products = styled_good_products.background_gradient(
                subset=['Écart de délai'], 
                cmap="RdYlGn_r",
                vmin=numeric_good_products['Écart de délai'].min(),
                vmax=0
            )
            
            st.dataframe(styled_good_products, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun produit avec un écart favorable trouvé dans cette période.")

    with product_tabs[1]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['negative']}; margin: 0;">Produits à améliorer (Écart > 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Formater les données pour l'affichage
        display_bad_products = bad_products[product_display_cols].copy()
        
        # S'assurer que les délais sont affichés avec un seul chiffre après la virgule
        for col in ['Délai théorique', 'Délai réel', 'Écart de délai']:
            if col in display_bad_products.columns:
                display_bad_products[col] = display_bad_products[col].map(lambda x: f"{x:.1f}" if pd.notnull(x) else x)
        
        # S'assurer que les numéros de commande sont des entiers sans décimales
        if 'Bon de commande' in display_bad_products.columns and display_bad_products['Bon de commande'].dtype != 'object':
            display_bad_products['Bon de commande'] = display_bad_products['Bon de commande'].astype(int)
        
        # Styliser le dataframe en combinant les couleurs par colonne et le gradient pour Écart
        if not display_bad_products.empty:
            styled_bad_products = display_bad_products.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Description du matériel' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == 'Bon de commande' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["negative"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart de délai' else
                f'background-color: {color_palette["positive" if x["Statut de livraison"] == "En avance" else "neutral" if x["Statut de livraison"] == "À temps" else "negative"]}30; font-weight: bold; color: {color_palette["text"]}'
                for col in display_bad_products.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart
            numeric_bad_products = bad_products[product_display_cols].copy()
            styled_bad_products = styled_bad_products.background_gradient(
                subset=['Écart de délai'], 
                cmap="RdYlGn_r",
                vmin=0,
                vmax=numeric_bad_products['Écart de délai'].max()
            )
            
            st.dataframe(styled_bad_products, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun produit avec un écart défavorable trouvé dans cette période.")
