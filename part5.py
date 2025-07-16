import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

def part_five(df, year, vendor_search):
    """
    Analyse des performances d'un fournisseur spécifique pour une année donnée
    
    Args:
        df: DataFrame contenant les données complètes
        year: Année sélectionnée
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


    
   
    '''
    # Filtrer par année
    mask_current = (supplier_data['Year'] == year)
    current_data = supplier_data[mask_current].copy()
    
    if current_data.empty:
        st.warning(f"Aucune donnée disponible pour {supplier_name} en {year}")
        return
    
    # Déterminer l'année précédente
    prev_year = year - 1
    
    # Filtrer les données pour l'année précédente
    mask_prev = (supplier_data['Year'] == prev_year)
    prev_data = supplier_data[mask_prev].copy()'''

    # Filtrer par année ET mois sélectionnés (remplacer le filtrage existant)
    mask_current = (supplier_data['Year'] == year) & (supplier_data['Month'].isin(st.session_state.selected_months))
    current_data = supplier_data[mask_current].copy()

    if current_data.empty:
        st.warning(f"Aucune donnée disponible pour {supplier_name} en {year} pour les mois sélectionnés")
        return

    # Pour la période de comparaison, utiliser les mêmes mois mais de l'année précédente
    prev_year = year - 1
    mask_prev = (supplier_data['Year'] == prev_year) & (supplier_data['Month'].isin(st.session_state.selected_months))
    prev_data = supplier_data[mask_prev].copy()
        


    # Utiliser un style personnalisé pour l'en-tête
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 10px; border-radius: 10px;">
        <h4 style="color: white; text-align: center;">Analyse annuelle du fournisseur: {supplier_name} (ID: {supplier_id})</h4>
        <h5 style="color: white; text-align: center;">Année {year}</h5>
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
    
    # Faire la même chose pour l'année précédente
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
        <h3 style="color: white;text-align: center;margin: 0;">Délais Moyens</h3>
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

    # --- SECTION 3: COMPARAISON AVEC L'ANNÉE PRÉCÉDENTE ---
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white; text-align: center; margin: 0;">Comparaison avec l'Année {prev_year}</h5>
    </div>
    """, unsafe_allow_html=True)

    if not prev_data.empty:
        # Calcul des indicateurs clés pour l'année précédente
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
            <h4 style="color:{color_palette['text']};">Évolution des volumes par rapport à l'année {prev_year}:</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            change_color = color_palette['positive'] if order_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Nombre de commandes: {prev_total_orders} → {total_orders}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{order_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            change_color = color_palette['positive'] if product_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Nombre de références: {prev_total_products} → {total_products}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{product_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            change_color = color_palette['positive'] if product_count_change >= 0 else color_palette['negative']
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; text-align:center;">
                <p style="margin:0;">Nombre de lignes: {prev_total_products_count} → {total_products_count}</p>
                <h5 style="color:{change_color}; margin:5px 0 0 0;">{product_count_change:+.1f}%</h5>
            </div>
            """, unsafe_allow_html=True)
        
        # Calcul des délais moyens pour les commandes de l'année précédente
        if not prev_orders.empty:
            prev_orders['Écart_commande (jours)'] = (prev_orders['Délai réel'] - prev_orders['Délai théorique']).round(1)
            
            prev_order_delay_means = {
                'Théorique': prev_orders['Délai théorique'].mean().round(1),
                'Réel': prev_orders['Délai réel'].mean().round(1),
                'Écart': prev_orders['Écart_commande (jours)'].mean().round(1)
            }
            
            # Calcul des délais moyens pour les produits de l'année précédente
            prev_data['Écart de délai'] = (prev_data['Délai réel'] - prev_data['Délai théorique']).round(1)
            
            prev_product_delay_means = {
                'Théorique': prev_data['Délai théorique'].mean().round(1),
                'Réel': prev_data['Délai réel'].mean().round(1),
                'Écart': prev_data['Écart de délai'].mean().round(1)
            }
            
            # Évolution des délais
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-top: 15px;">
                <h4 style="color:{color_palette['text']};">Évolution des délais par rapport à l'année {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)

            # Création de tableaux pour l'évolution des délais
            tab1, tab2 = st.tabs(["Délais par commande", "Délais par produit"])

            # Onglet Délais par commande
            with tab1:
                # Préparation des données pour le tableau d'évolution des commandes
                order_evolution = pd.DataFrame({
                    'Type': ['Théorique', 'Réel', 'Écart'],
                    f'Actuel ({year})': [
                        round(order_delay_means['Théorique'], 1), 
                        round(order_delay_means['Réel'], 1), 
                        round(order_delay_means['Écart'], 1)
                    ],
                    f'Précédent ({prev_year})': [
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
                
                # Fonction pour colorer les colonnes
                def highlight_columns_order(x):
                    df_styler = pd.DataFrame('', index=x.index, columns=x.columns)
                    df_styler['Type'] = 'background-color: #f5f5f5'
                    df_styler[f'Actuel ({year})'] = f'background-color: {color_palette["primary"]}; color: white'
                    df_styler[f'Précédent ({prev_year})'] = f'background-color: {color_palette["secondary"]}; color: white'
                    df_styler['Évolution (jours)'] = 'background-color: #e1f5fe'
                    return df_styler
                
                # Appliquer le style au DataFrame
                styled_order_evolution = order_evolution.style.apply(
                    highlight_columns_order, axis=None
                ).map(
                    highlight_evolution, subset=['Évolution (jours)']
                ).format({
                    f'Actuel ({year})': '{:.1f}',
                    f'Précédent ({prev_year})': '{:.1f}',
                    'Évolution (jours)': '{:.1f}'
                })
                
                # Afficher le tableau
                st.dataframe(styled_order_evolution, use_container_width=True, hide_index=True)

            # Onglet Délais par produit
            with tab2:
                # Préparation des données pour le tableau d'évolution des produits
                product_evolution = pd.DataFrame({
                    'Type': ['Théorique', 'Réel', 'Écart'],
                    f'Actuel ({year})': [
                        round(product_delay_means['Théorique'], 1), 
                        round(product_delay_means['Réel'], 1), 
                        round(product_delay_means['Écart'], 1)
                    ],
                    f'Précédent ({prev_year})': [
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
                ).map(
                    highlight_evolution, subset=['Évolution (jours)']
                ).format({
                    f'Actuel ({year})': '{:.1f}',
                    f'Précédent ({prev_year})': '{:.1f}',
                    'Évolution (jours)': '{:.1f}'
                })
                
                # Afficher le tableau
                st.dataframe(styled_product_evolution, use_container_width=True, hide_index=True)

    else:
        st.info(f"Aucune donnée disponible pour l'année {prev_year} pour comparaison")
    
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
            title=f"Répartition des commandes en {year}",
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
        # Comparaison avec l'année précédente si des données sont disponibles
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
                    f'% {prev_year}': f"{prev_pct:.1f}%",
                    'Évolution': f"{evolution:+.1f}%",
                    'color': evolution_color
                })
                        
            comparison_df = pd.DataFrame(comparison_data)
            
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
                <h4 style="color:{color_palette['text']};">Comparaison avec l'année {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher le tableau avec des couleurs personnalisées
            for i, row in comparison_df.iterrows():
                col1, col2, col3 = st.columns([2.5, 1.5, 1.5])
                with col1:
                    st.markdown(f"<div style='font-weight:bold;'>{row['Statut']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"{row[f'% {prev_year}']}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div style='color:{row['color']};font-weight:bold;'>{row['Évolution']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Aucune donnée disponible pour l'année {prev_year}")

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
            title=f"Répartition des produits en {year}",
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
        # Comparaison avec l'année précédente si des données sont disponibles
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
                    f'% {prev_year}': f"{prev_pct:.1f}%",
                    'Évolution': f"{evolution:+.1f}%",
                    'color': evolution_color
                })
            
            comparison_df_products = pd.DataFrame(comparison_data_products)
            
            st.markdown(f"""
            <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
                <h4 style="color:{color_palette['text']};">Comparaison avec l'année {prev_year}:</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Afficher le tableau avec des couleurs personnalisées
            for i, row in comparison_df_products.iterrows():
                col1, col2, col3 = st.columns([2.5, 1.5, 1.5])
                with col1:
                    st.markdown(f"<div style='font-weight:bold;'>{row['Statut']}</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"{row[f'% {prev_year}']}", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div style='color:{row['color']};font-weight:bold;'>{row['Évolution']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Aucune donnée disponible pour l'année {prev_year}")

    # --- SECTION 5: TOP ET PIRES PRODUITS PAR ÉCART ---
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
    
    # 1. Renommer les colonnes dans current_data
    current_data = current_data.rename(columns={
        'Document Date': 'Doc Date',
        'Order Quantity': 'Order Qty'
    })
    # Colonnes à afficher pour les produits
    product_display_cols = [
        'Matériel', 'Description du matériel', 'Bon de commande', 'Doc Date', 'Order Qty',
        'Délai théorique', 'Délai réel', 'Écart de délai', 'Statut de livraison'
    ]

    product_tabs = st.tabs([f"📈 Produits Performants en {year} (Écart ≤ 0)", f"📉 Produits à Améliorer en {year} (Écart > 0)"])

    with product_tabs[0]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['positive']}; margin: 0;">Meilleurs Produits de l'année {year} (Écart ≤ 0)</h6>
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
        # Formater Doc Date (afficher seulement la date)

        if 'Doc Date' in display_good_products.columns:
            display_good_products['Doc Date'] = pd.to_datetime(display_good_products['Doc Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Formater Order Qty (2 chiffres après la virgule)
        if 'Order Qty' in display_good_products.columns:
            display_good_products['Order Qty'] = display_good_products['Order Qty'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")

        
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
                if col == 'Doc Date' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}'
                if col == 'Order Qty' else
                f'background-color: {color_palette["background"]}; color: {color_palette["text"]}'
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
            st.info(f"Aucun produit avec un écart favorable trouvé pour l'année {year}.")

    with product_tabs[1]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['negative']}; margin: 0;">Produits à améliorer de l'année {year} (Écart > 0)</h6>
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
        # Formater Doc Date 
        if 'Doc Date' in display_bad_products.columns:
            display_bad_products['Doc Date'] = pd.to_datetime(display_bad_products['Doc Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Formater Order Qty (2 chiffres après la virgule)
        if 'Order Qty' in display_bad_products.columns:
            display_bad_products['Order Qty'] = display_bad_products['Order Qty'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
        
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
                if col == 'Doc Date' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}'
                if col == 'Order Qty' else
                f'background-color: {color_palette["background"]}; color: {color_palette["text"]}'
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
            st.info(f"Aucun produit avec un écart défavorable trouvé pour l'année {year}.")


    # --- SECTION 6: ANALYSE AGREGÉE PAR PRODUIT ---
    st.markdown(f"""
    <div style="background-color:{color_palette['tertiary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center;margin: 0;">Analyse par Produit</h5>
    </div>
    """, unsafe_allow_html=True)

    # Grouper les données par Matériel pour calculer les moyennes et pourcentages
    product_agg = current_data.groupby(['Matériel', 'Description du matériel', 'Matériel du fournisseur']).agg({
        'Bon de commande': 'nunique',
        'Délai théorique': 'mean',
        'Délai réel': 'mean',
        'Écart de délai': 'mean'
    }).reset_index()
    product_agg = product_agg.rename(columns={'Bon de commande': 'Nbre de commandes'})  

    # Arrondir les valeurs à un chiffre après la virgule
    product_agg['Délai théorique'] = product_agg['Délai théorique'].round(1)
    product_agg['Délai réel'] = product_agg['Délai réel'].round(1)
    product_agg['Écart de délai'] = product_agg['Écart de délai'].round(1)

    # Calculer les pourcentages de statuts pour chaque produit
    status_percentages = current_data.groupby('Matériel')['Statut de livraison'].value_counts(normalize=True).unstack().fillna(0) * 100
    status_percentages = status_percentages.round(1)

    # S'assurer que toutes les colonnes existent, sinon les créer avec des zéros
    for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
        if status not in status_percentages.columns:
            status_percentages[status] = 0

    # Renommer les colonnes pour plus de clarté
    status_percentages = status_percentages.rename(columns={
        'En avance': '% En avance',
        'À temps': '% À temps',
        'Retard accepté': '% Retard accepté',
        'Long délai': '% Long délai'
    })

    # Joindre les pourcentages au DataFrame agrégé
    product_agg = pd.merge(product_agg, status_percentages, left_on='Matériel', right_index=True, how='left')

    # Remplir les NaN avec des zéros pour les pourcentages
    percentage_columns = ['% En avance', '% À temps', '% Retard accepté', '% Long délai']
    product_agg[percentage_columns] = product_agg[percentage_columns].fillna(0)

    # Séparer les produits en bons et mauvais selon l'écart moyen
    good_products_agg = product_agg[product_agg['Écart de délai'] <= 0].sort_values('Écart de délai').copy()
    bad_products_agg = product_agg[product_agg['Écart de délai'] > 0].sort_values('Écart de délai', ascending=False).copy()

    # Créer des onglets pour les afficher
    product_agg_tabs = st.tabs([f"📈 Produits Performants (Écart moyen ≤ 0)", f"📉 Produits à Améliorer (Écart moyen > 0)"])

    # Premier onglet: Produits performants
    with product_agg_tabs[0]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['positive']}; margin: 0;">Statistiques des produits performants (Écart moyen ≤ 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        if not good_products_agg.empty:
            # Formater les données pour l'affichage
            display_good_agg = good_products_agg.copy()
            
            # Styliser le dataframe
            styled_good_agg = display_good_agg.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Description du matériel' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel du fournisseur' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}'
                if col == 'Nombre de commandes' else  # CETTE LIGNE VIENT MAINTENANT ICI
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}'
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["positive"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart de délai' else
                f'background-color: {color_palette["positive"]}30; color: {color_palette["text"]}' 
                if col == '% En avance' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == '% À temps' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == '% Retard accepté' else
                f'background-color: {color_palette["negative"]}30; color: {color_palette["text"]}'
                for col in display_good_agg.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart de délai
            styled_good_agg = styled_good_agg.background_gradient(
                subset=['Écart de délai'], 
                cmap="RdYlGn_r",
                vmin=display_good_agg['Écart de délai'].min(),
                vmax=0
            )
            
            # Formater les nombres
            styled_good_agg = styled_good_agg.format({
                'Délai théorique': '{:.1f}',
                'Délai réel': '{:.1f}',
                'Écart de délai': '{:.1f}',
                '% En avance': '{:.1f}%',
                '% À temps': '{:.1f}%',
                '% Retard accepté': '{:.1f}%',
                '% Long délai': '{:.1f}%'
            })
            
            st.dataframe(styled_good_agg, use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucun produit avec un écart moyen favorable trouvé pour l'année {year}.")

    # Deuxième onglet: Produits à améliorer
    with product_agg_tabs[1]:
        st.markdown(f"""
        <div style="padding: 5px; border-radius: 5px;">
            <h6 style="color:{color_palette['negative']}; margin: 0;">Statistiques des produits à améliorer (Écart moyen > 0)</h6>
        </div>
        """, unsafe_allow_html=True)
        
        if not bad_products_agg.empty:
            # Formater les données pour l'affichage
            display_bad_agg = bad_products_agg.copy()
            
            # Styliser le dataframe
            styled_bad_agg = display_bad_agg.style.apply(lambda x: [
                f'background-color: {color_palette["primary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Description du matériel' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == 'Matériel du fournisseur' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}'
                if col == 'Nombre de commandes' else  # CETTE LIGNE VIENT MAINTENANT ICI
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}'
                if col == 'Délai théorique' else
                f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
                if col == 'Délai réel' else
                f'background-color: {color_palette["negative"]}30; font-weight: bold; color: {color_palette["text"]}' 
                if col == 'Écart de délai' else
                f'background-color: {color_palette["positive"]}30; color: {color_palette["text"]}' 
                if col == '% En avance' else
                f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
                if col == '% À temps' else
                f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
                if col == '% Retard accepté' else
                f'background-color: {color_palette["negative"]}30; color: {color_palette["text"]}'
                for col in display_bad_agg.columns
            ], axis=1)
            
            # Ajouter le gradient sur la colonne Écart de délai
            styled_bad_agg = styled_bad_agg.background_gradient(
                subset=['Écart de délai'], 
                cmap="RdYlGn_r",
                vmin=0,
                vmax=display_bad_agg['Écart de délai'].max()
            )
            
            # Formater les nombres
            styled_bad_agg = styled_bad_agg.format({
                'Délai théorique': '{:.1f}',
                'Délai réel': '{:.1f}',
                'Écart de délai': '{:.1f}',
                '% En avance': '{:.1f}%',
                '% À temps': '{:.1f}%',
                '% Retard accepté': '{:.1f}%',
                '% Long délai': '{:.1f}%'
            })
            
            st.dataframe(styled_bad_agg, use_container_width=True, hide_index=True)
        else:
            st.info(f"Aucun produit avec un écart moyen défavorable trouvé pour l'année {year}.")

    
    # --- SECTION 7: TABLEAUX MENSUELS POUR COMMANDES ET PRODUITS ---
    st.markdown(f"""
    <div style="background-color:{color_palette['primary']}; padding: 8px; border-radius: 8px; margin-top: 25px;">
        <h5 style="color: white;text-align: center;margin: 0;">Analyse Mensuelle</h5>
    </div>
    """, unsafe_allow_html=True)

    # Création des onglets pour séparer les tableaux des commandes et des produits
    monthly_tabs = st.tabs(["Commandes Mensuelles", "Produits Mensuels"])

    # Premier onglet: Analyse mensuelle des commandes
    with monthly_tabs[0]:
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
            <h6 style="color:{color_palette['text']};">Analyse mensuelle des commandes pour {year}</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Extraire le mois à partir de la date de comptabilisation
        current_orders['Mois'] = pd.to_datetime(current_orders['Date de comptabilisation']).dt.month
        
        # Créer un mapping pour les noms des mois en français
        month_names = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril', 5: 'Mai', 6: 'Juin',
            7: 'Juillet', 8: 'Août', 9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        
        # Appliquer le mapping pour obtenir les noms des mois
        current_orders['Nom du mois'] = current_orders['Mois'].map(month_names)
        
        # Grouper par mois et calculer les métriques mensuelles pour les commandes
        monthly_orders = current_orders.groupby('Mois').agg({
            'Bon de commande': 'nunique',  # Nombre de commandes uniques
            'Délai théorique': 'mean',     # Délai théorique moyen
            'Délai réel': 'mean',          # Délai réel moyen
            'Écart_commande (jours)': 'mean'  # Écart moyen
        }).reset_index()
        
        # Renommer les colonnes pour plus de clarté
        monthly_orders = monthly_orders.rename(columns={
            'Bon de commande': 'Nombre de commandes',
            'Écart_commande (jours)': 'Écart moyen'
        })
        
        # Arrondir les délais à un chiffre après la virgule
        monthly_orders['Délai théorique'] = monthly_orders['Délai théorique'].round(1)
        monthly_orders['Délai réel'] = monthly_orders['Délai réel'].round(1)
        monthly_orders['Écart moyen'] = monthly_orders['Écart moyen'].round(1)
        
        # Ajouter les noms des mois au DataFrame
        monthly_orders['Mois'] = monthly_orders['Mois'].map(month_names)
        
        # Calculer les pourcentages de statuts de livraison par mois
        status_by_month = pd.crosstab(current_orders['Mois'], current_orders['Statut livraison'], normalize='index') * 100
        
        # S'assurer que toutes les colonnes de statut existent
        for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
            if status not in status_by_month.columns:
                status_by_month[status] = 0
        
        # Arrondir les pourcentages à un chiffre après la virgule
        status_by_month = status_by_month.round(1)
        
        # Renommer les colonnes pour plus de clarté
        status_by_month = status_by_month.rename(columns={
            'En avance': '% En avance',
            'À temps': '% À temps',
            'Retard accepté': '% Retard accepté',
            'Long délai': '% Long délai'
        })
        
        # Réinitialiser l'index pour la fusion
        status_by_month = status_by_month.reset_index()
        
        # Fusionner les DataFrames
        monthly_orders_complete = pd.merge(monthly_orders, status_by_month, left_on='Mois', right_on=status_by_month['Mois'].map(month_names), how='left')
        
        # Réorganiser les colonnes pour une meilleure lisibilité
        columns_order = [
            'Mois', 'Nombre de commandes', 'Délai théorique', 'Délai réel', 'Écart moyen',
            '% En avance', '% À temps', '% Retard accepté', '% Long délai'
        ]
        
        # Sélectionner et réorganiser les colonnes
        monthly_orders_display = monthly_orders_complete[columns_order].copy()
        
        # Styliser le tableau des commandes mensuelles
        styled_monthly_orders = monthly_orders_display.style.apply(lambda x: [
            f'background-color: {color_palette["primary"]}30; font-weight: bold; color: {color_palette["text"]}' 
            if col == 'Mois' else
            f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
            if col == 'Nombre de commandes' else
            f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
            if col == 'Délai théorique' else
            f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
            if col == 'Délai réel' else
            f'background-color: {color_palette["positive" if x["Écart moyen"] <= 0 else "negative"]}30; font-weight: bold; color: {color_palette["text"]}' 
            if col == 'Écart moyen' else
            f'background-color: {color_palette["positive"]}30; color: {color_palette["text"]}' 
            if col == '% En avance' else
            f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
            if col == '% À temps' else
            f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
            if col == '% Retard accepté' else
            f'background-color: {color_palette["negative"]}30; color: {color_palette["text"]}'
            for col in monthly_orders_display.columns
        ], axis=1)
        
        # Ajouter le gradient sur la colonne Écart moyen
        styled_monthly_orders = styled_monthly_orders.background_gradient(
            subset=['Écart moyen'], 
            cmap="RdYlGn_r",
            vmin=monthly_orders_display['Écart moyen'].min() if monthly_orders_display['Écart moyen'].min() < 0 else -1,
            vmax=monthly_orders_display['Écart moyen'].max() if monthly_orders_display['Écart moyen'].max() > 0 else 1
        )
        
        # Formater les nombres
        styled_monthly_orders = styled_monthly_orders.format({
            'Nombre de commandes': '{:.0f}',
            'Délai théorique': '{:.1f}',
            'Délai réel': '{:.1f}',
            'Écart moyen': '{:.1f}',
            '% En avance': '{:.1f}%',
            '% À temps': '{:.1f}%',
            '% Retard accepté': '{:.1f}%',
            '% Long délai': '{:.1f}%'
        })
        
        # Afficher le tableau stylisé
        st.dataframe(styled_monthly_orders, use_container_width=True, hide_index=True)
        
        # Ajouter une visualisation pour les tendances mensuelles
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-top: 15px;">
            <h5 style="color:{color_palette['text']};">Tendances mensuelles des commandes</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # Convertir les noms des mois en numéros pour le tri
        month_to_num = {v: k for k, v in month_names.items()}
        monthly_orders_display['month_num'] = monthly_orders_display['Mois'].map(month_to_num)
        monthly_orders_sorted = monthly_orders_display.sort_values('month_num')
        monthly_orders_sorted = monthly_orders_sorted.drop('month_num', axis=1)
        
        # Créer le graphique des tendances des délais par mois
        fig_monthly_trends = go.Figure()
        
        # Ajouter les lignes pour les délais théoriques, réels et l'écart
        fig_monthly_trends.add_trace(go.Scatter(
            x=monthly_orders_sorted['Mois'],
            y=monthly_orders_sorted['Délai théorique'],
            mode='lines+markers',
            name='Délai théorique',
            line=dict(color=color_palette['neutral'], width=2),
            marker=dict(size=8)
        ))
        
        fig_monthly_trends.add_trace(go.Scatter(
            x=monthly_orders_sorted['Mois'],
            y=monthly_orders_sorted['Délai réel'],
            mode='lines+markers',
            name='Délai réel',
            line=dict(color=color_palette['tertiary'], width=2),
            marker=dict(size=8)
        ))
        
        fig_monthly_trends.add_trace(go.Scatter(
            x=monthly_orders_sorted['Mois'],
            y=monthly_orders_sorted['Écart moyen'],
            mode='lines+markers',
            name='Écart moyen',
            line=dict(color=color_palette['quaternary'], width=2, dash='dot'),
            marker=dict(size=8)
        ))
        
        # Mettre à jour la mise en page du graphique
        fig_monthly_trends.update_layout(
            title='Évolution des délais mensuels pour les commandes',
            xaxis_title='Mois',
            yaxis_title='Jours',
            legend_title='Métriques',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgrey'),
            yaxis=dict(gridcolor='lightgrey'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Ajouter une ligne horizontale à y=0 pour la référence
        fig_monthly_trends.add_shape(type="line",
            xref="paper", yref="y",
            x0=0, y0=0, x1=1, y1=0,
            line=dict(color="grey", width=1, dash="dash")
        )
        
        # Afficher le graphique
        st.plotly_chart(fig_monthly_trends, use_container_width=True)

    # Deuxième onglet: Analyse mensuelle des produits
    with monthly_tabs[1]:
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px;">
            <h6 style="color:{color_palette['text']};">Analyse mensuelle des produits pour {year}</h6>
        </div>
        """, unsafe_allow_html=True)
        
        # Extraire le mois à partir de la date de comptabilisation
        current_data['Mois'] = pd.to_datetime(current_data['Date de comptabilisation']).dt.month
        
        # Appliquer le mapping pour obtenir les noms des mois
        current_data['Nom du mois'] = current_data['Mois'].map(month_names)
        
        
        # Grouper par mois et calculer les métriques mensuelles pour les produits
        monthly_products = current_data.groupby('Mois').agg({
            'Matériel': ['nunique', 'count'],  # Nombre de produits uniques et nombre total de lignes
            'Délai théorique': 'mean',         # Délai théorique moyen
            'Délai réel': 'mean',              # Délai réel moyen
            'Écart de délai': 'mean'           # Écart moyen
        })

        # Aplatir les noms de colonnes multi-niveaux
        monthly_products.columns = ['Produits uniques', 'Nb de lignes', 'Délai théorique', 'Délai réel', 'Écart moyen']
        monthly_products = monthly_products.reset_index()
        # Arrondir les délais à un chiffre après la virgule
        monthly_products['Délai théorique'] = monthly_products['Délai théorique'].round(1)
        monthly_products['Délai réel'] = monthly_products['Délai réel'].round(1)
        monthly_products['Écart moyen'] = monthly_products['Écart moyen'].round(1)
        
        # Ajouter les noms des mois au DataFrame
        monthly_products['Mois'] = monthly_products['Mois'].map(month_names)
        
        # Calculer les pourcentages de statuts de livraison par mois pour les produits
        status_by_month_products = pd.crosstab(current_data['Mois'], current_data['Statut de livraison'], normalize='index') * 100
        
        # S'assurer que toutes les colonnes de statut existent
        for status in ['En avance', 'À temps', 'Retard accepté', 'Long délai']:
            if status not in status_by_month_products.columns:
                status_by_month_products[status] = 0
        
        # Arrondir les pourcentages à un chiffre après la virgule
        status_by_month_products = status_by_month_products.round(1)
        
        # Renommer les colonnes pour plus de clarté
        status_by_month_products = status_by_month_products.rename(columns={
            'En avance': '% En avance',
            'À temps': '% À temps',
            'Retard accepté': '% Retard accepté',
            'Long délai': '% Long délai'
        })
        
        # Réinitialiser l'index pour la fusion
        status_by_month_products = status_by_month_products.reset_index()
        
        # Fusionner les DataFrames
        monthly_products_complete = pd.merge(monthly_products, status_by_month_products, left_on='Mois', right_on=status_by_month_products['Mois'].map(month_names), how='left')
        
        # Réorganiser les colonnes pour une meilleure lisibilité
        columns_order_products = [
            'Mois', 'Produits uniques', 'Nb de lignes', 'Délai théorique', 'Délai réel', 'Écart moyen',
            '% En avance', '% À temps', '% Retard accepté', '% Long délai'
        ]
        
        # Sélectionner et réorganiser les colonnes
        monthly_products_display = monthly_products_complete[columns_order_products].copy()
        
        # Styliser le tableau des produits mensuels
        styled_monthly_products = monthly_products_display.style.apply(lambda x: [
            f'background-color: {color_palette["primary"]}30; font-weight: bold; color: {color_palette["text"]}' 
            if col == 'Mois' else
            f'background-color: {color_palette["secondary"]}30; color: {color_palette["text"]}' 
            if col == 'Produits uniques' else
            f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
            if col == 'Nb de lignes' else
            f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
            if col == 'Délai théorique' else
            f'background-color: {color_palette["tertiary"]}30; color: {color_palette["text"]}' 
            if col == 'Délai réel' else
            f'background-color: {color_palette["positive" if x["Écart moyen"] <= 0 else "negative"]}30; font-weight: bold; color: {color_palette["text"]}' 
            if col == 'Écart moyen' else
            f'background-color: {color_palette["positive"]}30; color: {color_palette["text"]}' 
            if col == '% En avance' else
            f'background-color: {color_palette["neutral"]}30; color: {color_palette["text"]}' 
            if col == '% À temps' else
            f'background-color: {color_palette["quaternary"]}30; color: {color_palette["text"]}' 
            if col == '% Retard accepté' else
            f'background-color: {color_palette["negative"]}30; color: {color_palette["text"]}'
            for col in monthly_products_display.columns
        ], axis=1)
        
        # Ajouter le gradient sur la colonne Écart moyen
        styled_monthly_products = styled_monthly_products.background_gradient(
            subset=['Écart moyen'], 
            cmap="RdYlGn_r",
            vmin=monthly_products_display['Écart moyen'].min() if monthly_products_display['Écart moyen'].min() < 0 else -1,
            vmax=monthly_products_display['Écart moyen'].max() if monthly_products_display['Écart moyen'].max() > 0 else 1
        )
        
        # Formater les nombres
        styled_monthly_products = styled_monthly_products.format({
            'Produits uniques': '{:.0f}',
            'Nb de lignes': '{:.0f}',
            'Délai théorique': '{:.1f}',
            'Délai réel': '{:.1f}',
            'Écart moyen': '{:.1f}',
            '% En avance': '{:.1f}%',
            '% À temps': '{:.1f}%',
            '% Retard accepté': '{:.1f}%',
            '% Long délai': '{:.1f}%'
        })
        
        # Afficher le tableau stylisé
        st.dataframe(styled_monthly_products, use_container_width=True, hide_index=True)
        
        # Ajouter une visualisation pour les tendances mensuelles des produits
        st.markdown(f"""
        <div style="background-color:{color_palette['background']}; padding: 10px; border-radius: 8px; margin-top: 15px;">
            <h5 style="color:{color_palette['text']};">Tendances mensuelles des produits</h5>
        </div>
        """, unsafe_allow_html=True)
        
        # Convertir les noms des mois en numéros pour le tri
        month_to_num = {v: k for k, v in month_names.items()}
        monthly_products_display['month_num'] = monthly_products_display['Mois'].map(month_to_num)
        monthly_products_sorted = monthly_products_display.sort_values('month_num')
        monthly_products_sorted = monthly_products_sorted.drop('month_num', axis=1)
        
        # Créer le graphique des tendances des délais par mois pour les produits
        fig_monthly_trends_products = go.Figure()
        
        # Ajouter les lignes pour les délais théoriques, réels et l'écart
        fig_monthly_trends_products.add_trace(go.Scatter(
            x=monthly_products_sorted['Mois'],
            y=monthly_products_sorted['Délai théorique'],
            mode='lines+markers',
            name='Délai théorique',
            line=dict(color=color_palette['neutral'], width=2),
            marker=dict(size=8)
        ))
        
        fig_monthly_trends_products.add_trace(go.Scatter(
            x=monthly_products_sorted['Mois'],
            y=monthly_products_sorted['Délai réel'],
            mode='lines+markers',
            name='Délai réel',
            line=dict(color=color_palette['tertiary'], width=2),
            marker=dict(size=8)
        ))
        
        fig_monthly_trends_products.add_trace(go.Scatter(
            x=monthly_products_sorted['Mois'],
            y=monthly_products_sorted['Écart moyen'],
            mode='lines+markers',
            name='Écart moyen',
            line=dict(color=color_palette['quaternary'], width=2, dash='dot'),
            marker=dict(size=8)
        ))
        
        # Mettre à jour la mise en page du graphique
        fig_monthly_trends_products.update_layout(
            title='Évolution des délais mensuels pour les produits',
            xaxis_title='Mois',
            yaxis_title='Jours',
            legend_title='Métriques',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(gridcolor='lightgrey'),
            yaxis=dict(gridcolor='lightgrey'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Ajouter une ligne horizontale à y=0 pour la référence
        fig_monthly_trends_products.add_shape(type="line",
            xref="paper", yref="y",
            x0=0, y0=0, x1=1, y1=0,
            line=dict(color="grey", width=1, dash="dash")
        )
        
        # Afficher le graphique
        st.plotly_chart(fig_monthly_trends_products, use_container_width=True)
