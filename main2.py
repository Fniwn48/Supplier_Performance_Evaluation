import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from part1 import *
from part2 import *
from part5 import *
from part4 import *
from part3 import *
from load1 import *
from part1_one import *
from part1_two import *
from part1_three import *
from part1_four import *
from gamme import *
from part1_five import *
from file1 import *
from part22 import *

st.set_page_config(layout="wide",page_title="Suivi de la Performance Fournisseur ⭐")


def main():
    apply_custom_theme()
    
    # Initialiser l'état de session pour tracker si les fichiers ont été importés
    if 'files_uploaded' not in st.session_state:
        st.session_state.files_uploaded = False
        
    # En-tête avec style amélioré et nouveau titre
    
    st.markdown("<h2 style='text-align: center; color: #1E88E5;'>Performance Logistique et Achats Fournisseurs</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Suivi des livraisons et performances des fournisseurs</p>", unsafe_allow_html=True)
    
    # Variables pour stocker les dataframes
    df1 = None
    df2 = None
    
    # Afficher la section d'importation uniquement si les fichiers n'ont pas encore été importés
    if not st.session_state.files_uploaded:
        # Uploader de fichier avec design amélioré
        with st.container():
            st.markdown("""
            <div style="background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 20px;">
            <h5 style="color: #4B5563; margin-top: 0;">Importation de données</h5>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<p>Fichier des délais de livraison:</p>", unsafe_allow_html=True)
                uploaded_file1 = st.file_uploader("Importez votre premier fichier Excel", type=["xlsx"], key="file1")
                
                st.markdown("<p>Fichier des gammes de produits:</p>", unsafe_allow_html=True)
                prodline_ref_file = st.file_uploader("Importez votre troisième fichier Excel", type=["xlsx"], key="file3")
            
            with col2:
                st.markdown("<p>Fichier des commandes:</p>", unsafe_allow_html=True)
                uploaded_file2 = st.file_uploader("Importez votre deuxième fichier Excel", type=["xlsx"], key="file2")
                
                st.markdown("<p>Fichier des produits VC:</p>", unsafe_allow_html=True)
                vc_file = st.file_uploader("Importez votre quatrième fichier Excel (produits VC)", type=["xlsx"], key="file4")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Vérifier si TOUS les fichiers sont présents avant de commencer le traitement
        if uploaded_file1 is not None and uploaded_file2 is not None and prodline_ref_file is not None and vc_file is not None:
            # Charger les fichiers
            df1 = load_and_validate_file1(uploaded_file1)
            if df1 is not None:
                df1 = add_prodline_name(df1, prodline_ref_file)
                df1 = add_vc_status(df1, vc_file)
            
            df2 = load_and_validate_file2(uploaded_file2, df1)
            if df2 is not None:
                df2 = add_prodline_name(df2, prodline_ref_file)
                df2 = add_vc_status(df2, vc_file)
            
            # Vérifier/ajouter la colonne Drop Statut si nécessaire
            if df1 is not None and "Drop Statut" not in df1.columns:
                df1["Drop Statut"] = "Non défini"
            if df2 is not None and "Drop Statut" not in df2.columns:
                df2["Drop Statut"] = "Non défini"
            
            # Si les deux fichiers sont chargés avec succès, mettre à jour l'état de session
            if df1 is not None and df2 is not None:
                st.session_state.files_uploaded = True
                st.session_state.df1 = df1
                st.session_state.df2 = df2
                # Rafraîchir la page pour masquer la section d'importation
                st.rerun()
        else:
            # Afficher un message indiquant quels fichiers manquent
            missing_files = []
            if uploaded_file1 is None:
                missing_files.append("Fichier des délais de livraison")
            if uploaded_file2 is None:
                missing_files.append("Fichier des commandes")
            if prodline_ref_file is None:
                missing_files.append("Fichier des gammes de produits")
            if vc_file is None:
                missing_files.append("Fichier des produits VC")
            
            if missing_files:
                st.info(f"En attente de : {', '.join(missing_files)}")
    else:
        # Récupérer les dataframes à partir de l'état de session
        df1 = st.session_state.df1
        df2 = st.session_state.df2
        
        # Bouton pour réinitialiser et permettre une nouvelle importation
        if st.sidebar.button("Réinitialiser les fichiers"):
            st.session_state.files_uploaded = False
            st.session_state.pop('df1', None)
            st.session_state.pop('df2', None)
            st.rerun()

    if df1 is not None and df2 is not None and st.session_state.files_uploaded:
        # Récupérer les années et mois uniques pour les filtres
        # Combiner les années des deux dataframes
        available_years1 = sorted(df1["Year"].unique())
        available_years2 = sorted(df2["Year"].unique())
        available_years = sorted(set(available_years1).intersection(set(available_years2)))
        
        # Filtres interactifs
        st.sidebar.markdown("<h2 style='color: #1E88E5;'>Filtres</h2>", unsafe_allow_html=True)
        
        # Filtre d'année (select au lieu de multiselect)
        year_options = [str(int(y)) for y in available_years]  # Convertir en entier pour éviter la virgule
        # Ajouter "Toutes les années" au début de la liste
        year_options = ["Toutes les années"] + year_options
        selected_year = st.sidebar.selectbox("Sélectionnez l'année", year_options)
        
        # Appliquer le filtre d'année aux deux dataframes
        if selected_year != "Toutes les années":
            year = int(selected_year)
            year_filtered_df1 = df1[df1["Year"] == year]
            year_filtered_df2 = df2[df2["Year"] == year]
            years = [year]
        else:
            year_filtered_df1 = df1
            year_filtered_df2 = df2
            years = []
            year = "Toutes"
        
        # Filtre de mois (select au lieu de multiselect)
        available_months = []
        month_names = {1:'Janvier', 2:'Février', 3:'Mars', 4:'Avril', 5:'Mai', 6:'Juin', 
                      7:'Juillet', 8:'Août', 9:'Septembre', 10:'Octobre', 11:'Novembre', 12:'Décembre'}
        
        if selected_year != "Toutes les années":
            # Trouver les mois disponibles dans les deux dataframes
            available_months1 = set(year_filtered_df1["Month"].unique())
            available_months2 = set(year_filtered_df2["Month"].unique())
            available_months = sorted(available_months1.intersection(available_months2))
            
            month_options = [f"{m} - {month_names[m]}" for m in available_months]
            # Ajouter "Tous les mois" au début de la liste
            month_options = ["Tous les mois"] + month_options
            selected_month_option = st.sidebar.selectbox("Sélectionnez le mois", month_options)
            
            if selected_month_option != "Tous les mois":
                month = int(selected_month_option.split(" - ")[0])
                month_filtered_df1 = year_filtered_df1[year_filtered_df1["Month"] == month]
                month_filtered_df2 = year_filtered_df2[year_filtered_df2["Month"] == month]
                months = [month]
            else:
                month_filtered_df1 = year_filtered_df1
                month_filtered_df2 = year_filtered_df2
                month = "Tous"
        else:
            # Si aucune année spécifique n'est sélectionnée, afficher un message explicatif
            st.sidebar.markdown(
                """
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; border-left: 5px solid #1E88E5; margin: 10px 0;">
                <p style="margin: 0; color: #0d47a1;">Veuillez sélectionner une année pour filtrer par mois</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            month_filtered_df1 = year_filtered_df1
            month_filtered_df2 = year_filtered_df2
            month = "Tous"
        
        # Liste déroulante des fournisseurs
        st.sidebar.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>Sélection fournisseur</h3>", unsafe_allow_html=True)
        
        # Obtenir les fournisseurs communs des deux dataframes filtrés
        vendors_df1 = set(month_filtered_df1["Nom du fournisseur"].unique())
        vendors_df2 = set(month_filtered_df2["Nom du fournisseur"].unique())
        common_vendors = sorted(vendors_df1.intersection(vendors_df2))
        
        # Si pas de fournisseurs communs, prendre tous les fournisseurs
        all_vendors = sorted([str(vendor) for vendor in list(vendors_df1.union(vendors_df2))])
        vendor_list = common_vendors if common_vendors else all_vendors
        
        # Ajouter "Tous les fournisseurs" au début de la liste
        vendor_options = ["Tous les fournisseurs"] + vendor_list
        selected_vendor = st.sidebar.selectbox("Choisissez un fournisseur", vendor_options)
        # Filtre de période - affiché seulement si une année ET un fournisseur sont sélectionnés
        if selected_year != "Toutes les années" and selected_vendor != "Tous les fournisseurs" and month == "Tous":
            st.sidebar.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>Période</h3>", unsafe_allow_html=True)
            setup_period_filter(int(selected_year))
        else:
            # Valeurs par défaut si aucune année n'est sélectionnée
            st.session_state.start_month = 1
            st.session_state.end_month = 12
            st.session_state.selected_months = list(range(1, 13))        

        # Filtre de gamme de produit - Maintenant permis sans sélection préalable
        st.sidebar.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>Gamme de produit</h3>", unsafe_allow_html=True)
        
        # Obtenir toutes les gammes de produits disponibles (pour tous les filtres)
        all_prodlines_df1 = set(df1["Prodline Name"].dropna().unique())
        all_prodlines_df2 = set(df2["Prodline Name"].dropna().unique())
        all_common_prodlines = sorted(all_prodlines_df1.intersection(all_prodlines_df2))
        all_prodlines = sorted(list(all_prodlines_df1.union(all_prodlines_df2)))
        all_prodline_list = all_common_prodlines if all_common_prodlines else all_prodlines
        
        # Ajouter "Toutes les gammes" au début de la liste
        prodline_options = ["Toutes les gammes"] + all_prodline_list
        selected_prodline = st.sidebar.selectbox("Choisissez une gamme de produit", prodline_options)
        
        # Initialiser selected_vc_types
        selected_vc_types = []
        
        # Appliquer les filtres sélectionnés
        if selected_vendor != "Tous les fournisseurs":
            # Filtrer par fournisseur
            vendor_filtered_df1 = month_filtered_df1[month_filtered_df1["Nom du fournisseur"] == selected_vendor]
            vendor_filtered_df2 = month_filtered_df2[month_filtered_df2["Nom du fournisseur"] == selected_vendor]
        else:
            vendor_filtered_df1 = month_filtered_df1
            vendor_filtered_df2 = month_filtered_df2
        
        # Appliquer le filtre de gamme de produit
        if selected_prodline != "Toutes les gammes":
            prodline_filtered_df1 = vendor_filtered_df1[vendor_filtered_df1["Prodline Name"] == selected_prodline]
            prodline_filtered_df2 = vendor_filtered_df2[vendor_filtered_df2["Prodline Name"] == selected_prodline]
        else:
            prodline_filtered_df1 = vendor_filtered_df1
            prodline_filtered_df2 = vendor_filtered_df2
            
        # Ajout du filtre Drop Statut - disponible uniquement si un autre filtre est sélectionné
        if selected_year != "Toutes les années" or selected_vendor != "Tous les fournisseurs" or selected_prodline != "Toutes les gammes":
            st.sidebar.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>Statut</h3>", unsafe_allow_html=True)
            
            # Obtenir les valeurs uniques de Drop Statut
            drop_status_values_df1 = set(prodline_filtered_df1["Drop Statut"].dropna().unique())
            drop_status_values_df2 = set(prodline_filtered_df2["Drop Statut"].dropna().unique())
            drop_status_values = sorted(drop_status_values_df1.union(drop_status_values_df2))
            
            # Ajouter "Tous les statuts" au début de la liste
            status_options = ["Tous les statuts"] + list(drop_status_values)
            selected_status = st.sidebar.selectbox("Choisissez un statut", status_options)
        else:
            # Si aucun autre filtre n'est sélectionné, désactiver ce filtre
            st.sidebar.markdown(
                """
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; border-left: 5px solid #1E88E5; margin: 10px 0;">
                <p style="margin: 0; color: #0d47a1;">Veuillez d'abord sélectionner une année, un fournisseur ou une gamme pour filtrer par statut</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            selected_status = "Tous les statuts"
        
        # Appliquer le filtre de statut
        if selected_status != "Tous les statuts":
            status_filtered_df1 = prodline_filtered_df1[prodline_filtered_df1["Drop Statut"] == selected_status]
            status_filtered_df2 = prodline_filtered_df2[prodline_filtered_df2["Drop Statut"] == selected_status]
        else:
            status_filtered_df1 = prodline_filtered_df1
            status_filtered_df2 = prodline_filtered_df2
            
        # Filtre Type VC - disponible uniquement si un autre filtre est sélectionné
        if selected_year != "Toutes les années" or selected_vendor != "Tous les fournisseurs" or selected_prodline != "Toutes les gammes" or selected_status != "Tous les statuts":
            st.sidebar.markdown("<h3 style='color: #1E88E5; margin-top: 20px;'>Type VC</h3>", unsafe_allow_html=True)
            
            # Vérifier si la colonne Type VC existe et obtenir les valeurs uniques
            if "Type VC" in df1.columns and "Type VC" in df2.columns:
                vc_values_df1 = set(status_filtered_df1["Type VC"].dropna().unique())
                vc_values_df2 = set(status_filtered_df2["Type VC"].dropna().unique())
                vc_values = sorted(vc_values_df1.union(vc_values_df2))
                
                # Multiselect pour permettre la sélection multiple
                selected_vc_types = st.sidebar.multiselect(
                    "Sélectionnez le(s) type(s)", 
                    vc_values,
                    default=vc_values  # Par défaut, tous sont sélectionnés
                )
        else:
            # Si aucun autre filtre n'est sélectionné, désactiver ce filtre
            st.sidebar.markdown(
                """
                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px; border-left: 5px solid #1E88E5; margin: 10px 0;">
                <p style="margin: 0; color: #0d47a1;">Veuillez d'abord sélectionner un autre filtre pour filtrer par type VC</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # Appliquer le filtre Type VC avec multiselect
        if selected_vc_types and "Type VC" in status_filtered_df1.columns and "Type VC" in status_filtered_df2.columns:
            filtered_df1 = status_filtered_df1[status_filtered_df1["Type VC"].isin(selected_vc_types)]
            filtered_df2 = status_filtered_df2[status_filtered_df2["Type VC"].isin(selected_vc_types)]
        else:
            filtered_df1 = status_filtered_df1
            filtered_df2 = status_filtered_df2
        
        # Gérer le cas où le filtre ne retourne aucune donnée
        if filtered_df1.empty or filtered_df2.empty:
            st.warning("Aucune donnée disponible avec les filtres actuels.")
        
        # Ajouter CSS pour colorer les tables
        st.markdown("""
        <style>
        /* Style pour les tableaux avec coloration sophistiquée */
        .dataframe-container .stDataFrame table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .dataframe-container .stDataFrame table thead tr th {
            background: linear-gradient(135deg, #1E88E5, #1565C0);
            color: white !important;
            font-weight: bold;
            padding: 12px 15px !important;
            text-align: left;
            border-bottom: none !important;
        }
        
        .dataframe-container .stDataFrame table tbody tr:nth-child(odd) {
            background-color: rgba(230, 242, 255, 0.6);
        }
        
        .dataframe-container .stDataFrame table tbody tr:nth-child(even) {
            background-color: rgba(213, 232, 255, 0.3);
        }
        
        .dataframe-container .stDataFrame table tbody tr:hover {
            background-color: rgba(66, 165, 245, 0.1);
        }
        
        .dataframe-container .stDataFrame table tbody tr td {
            padding: 10px 15px !important;
            border-bottom: 1px solid #E0E0E0 !important;
            color: #455A64;
        }
        
        /* Styles pour les colonnes spécifiques - couleurs sophistiquées */
        .dataframe-container .stDataFrame table tbody tr td:nth-child(1) {
            color: #1E88E5;
            font-weight: bold;
        }
        
        .dataframe-container .stDataFrame table tbody tr td:nth-child(2) {
            color: #7B1FA2;
        }
        
        .dataframe-container .stDataFrame table tbody tr td:nth-child(3) {
            color: #00897B;
        }
        
        .dataframe-container .stDataFrame table tbody tr td:nth-child(4) {
            color: #D81B60;
        }
        
        .dataframe-container .stDataFrame table tbody tr td:nth-child(5) {
            color: #6A1B9A;
        }
        
        .dataframe-container .stDataFrame table tbody tr td:nth-child(6) {
            color: #00695C;
        }
        
        /* Style pour les cartes métriques */
        .equal-height-cols .stMetric {
            background: linear-gradient(145deg, #ffffff, #f5f7fa);
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            padding: 15px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .equal-height-cols .stMetric:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Déterminer quel mode d'affichage utiliser en fonction des filtres sélectionnés
        if (selected_prodline != "Toutes les gammes" and 
            selected_vendor == "Tous les fournisseurs" and 
            selected_year == "Toutes les années"):
            # Filtrer les DataFrames complets par la gamme sélectionnée
            gamme_df2 = filtered_df2
            # Ajout du statut sélectionné au titre si applicable
            if selected_status != "Tous les statuts":
                st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
            if selected_vc_types and len(selected_vc_types) < len(vc_values):
                st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
            # Appel à la fonction d'analyse de gamme
            analyser_gamme(gamme_df2, selected_prodline)
            
        # Affichage des résultats en fonction des filtres existants
        elif selected_year != "Toutes les années" and month != "Tous" and selected_vendor != "Tous les fournisseurs":
            # Vue 3: Année, mois et fournisseur spécifiques
            # Ajout du titre de la gamme si sélectionnée
            if selected_prodline != "Toutes les gammes":
                st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
            # Ajout du statut sélectionné
            if selected_status != "Tous les statuts":
                st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
            if selected_vc_types and len(selected_vc_types) < len(vc_values):
                st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
            # Création d'un DataFrame spécial pour part_three
            special_df1_part3 = df1.copy()
            if selected_status != "Tous les statuts":
                special_df1_part3 = special_df1_part3[special_df1_part3["Drop Statut"] == selected_status]
            if selected_prodline != "Toutes les gammes":
                special_df1_part3 = special_df1_part3[special_df1_part3["Prodline Name"] == selected_prodline]
            if selected_vc_types and "Type VC" in special_df1_part3.columns:
                special_df1_part3 = special_df1_part3[special_df1_part3["Type VC"].isin(selected_vc_types)]

            part_three(special_df1_part3, year, month, selected_vendor)
            part1_three(filtered_df2, year, month, selected_vendor)

            if selected_prodline == "Toutes les gammes":
                camembert3(filtered_df2, year, month, selected_vendor)
        elif selected_vendor != "Tous les fournisseurs":
            # Mode fournisseur spécifique
            if selected_year == "Toutes les années":
                # Fournisseur sur toutes les années (Vue 4)
                if selected_prodline != "Toutes les gammes":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
                # Ajout du statut sélectionné
                if selected_status != "Tous les statuts":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
                if selected_vc_types and len(selected_vc_types) < len(vc_values):
                    st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
                part_four(filtered_df1, selected_vendor)
                part1_four(filtered_df2, selected_vendor)
                if selected_prodline == "Toutes les gammes":
                    camembert4(filtered_df2, selected_vendor)

            elif month == "Tous":
                # Fournisseur sur une année spécifique (Vue 5)
                if selected_prodline != "Toutes les gammes":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
                # Ajout du statut sélectionné
                if selected_status != "Tous les statuts":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
                if selected_vc_types and len(selected_vc_types) < len(vc_values):
                    st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
                # Création d'un DataFrame spécial pour part_five
                special_df1_part5 = df1.copy()
                if selected_status != "Tous les statuts":
                    special_df1_part5 = special_df1_part5[special_df1_part5["Drop Statut"] == selected_status]
                if selected_prodline != "Toutes les gammes":
                    special_df1_part5 = special_df1_part5[special_df1_part5["Prodline Name"] == selected_prodline]
                if selected_vc_types and "Type VC" in special_df1_part5.columns:
                    special_df1_part5 = special_df1_part5[special_df1_part5["Type VC"].isin(selected_vc_types)]

                # Création d'un DataFrame spécial pour part1_five (à partir de df2 complet)
                special_df2_part1_five = df2.copy()
                if selected_status != "Tous les statuts":
                    special_df2_part1_five = special_df2_part1_five[special_df2_part1_five["Drop Statut"] == selected_status]
                if selected_prodline != "Toutes les gammes":
                    special_df2_part1_five = special_df2_part1_five[special_df2_part1_five["Prodline Name"] == selected_prodline]
                if selected_vc_types and "Type VC" in special_df2_part1_five.columns:
                    special_df2_part1_five = special_df2_part1_five[special_df2_part1_five["Type VC"].isin(selected_vc_types)]

                # Fusionner les DataFrames AVANT d'appeler part_five
                special_df1_part5 = merge_df(special_df1_part5, special_df2_part1_five)


                # Utilisez ce DataFrame spécial
                # setup_period_filter(year)
                part_five(special_df1_part5, year, selected_vendor)
                part1_five(special_df2_part1_five, year, selected_vendor)
                if selected_prodline == "Toutes les gammes":
                    camembert5(filtered_df2, year, selected_vendor)
            else:
                # Mois et année spécifiques pour un fournisseur
                if selected_prodline != "Toutes les gammes":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
                # Ajout du statut sélectionné
                if selected_status != "Tous les statuts":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
                if selected_vc_types and len(selected_vc_types) < len(vc_values):
                    st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
                part_two(filtered_df1, year, month)
                part1_two(filtered_df2, year, month)
                if selected_prodline == "Toutes les gammes":
                    camembert2(filtered_df2, year, month)

        else:
            # Mode standard (sans fournisseur spécifique)
            if selected_year != "Toutes les années" and month != "Tous":
                # Vue 2: Année et mois spécifiques
                if selected_prodline != "Toutes les gammes":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
                # Ajout du statut sélectionné
                if selected_status != "Tous les statuts":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
                if selected_vc_types and len(selected_vc_types) < len(vc_values):
                    st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
                part_two(filtered_df1, year, month)
                part1_two(filtered_df2, year, month)
                if selected_prodline == "Toutes les gammes":
                    camembert2(filtered_df2, year, month)

            elif selected_year != "Toutes les années":
                # Vue 1: Année spécifique
                if selected_prodline != "Toutes les gammes":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Gamme de produit: {selected_prodline}</h6>", unsafe_allow_html=True)
                # Ajout du statut sélectionné
                if selected_status != "Tous les statuts":
                    st.markdown(f"<h6 style='color: #1E88E5;'>Statut: {selected_status}</h6>", unsafe_allow_html=True)
                if selected_vc_types and len(selected_vc_types) < len(vc_values):
                    st.markdown(f"<h6 style='color: #1E88E5;'>Type(s): {', '.join(selected_vc_types)}</h6>", unsafe_allow_html=True)
                part_one(filtered_df1, year)
                part1_one(filtered_df2, year)
                if selected_prodline == "Toutes les gammes":
                    camembert1(filtered_df2, year)

            else:
                 
                st.markdown("<h4 style='color: #1E88E5;'>Fichier 1: Délais de livraison</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 5px solid #4caf50; margin: 15px 0;">
                    <p style="margin: 0; color: #1b5e20;">✓ Base de données chargée avec succès: <b>{df1.shape[0]}</b> lignes et <b>{df1.shape[1]}</b> colonnes</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Résumé pour le fichier 1
                years_summary1 = df1.groupby("Year").agg(
                    nb_vendors=("Fournisseur", "nunique"),
                    nb_orders=("Bon de commande", "nunique"),
                    nb_materials=("Matériel", "nunique"),
                    nb_lignes=("Matériel", "count")
                ).reset_index()
                
                st.markdown("<h5 style='color: #1E88E5; margin-top: 20px;'>Résumé</h5>", unsafe_allow_html=True)
                st.markdown("<h6 style='color: #000000; margin-top: 20px;'>Le matériel Y4950100 est exclu de ce fichier</h6>", unsafe_allow_html=True)

                
                # Assurer que les métriques ont la même taille avec div.equal-height-cols
                st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
                # Affichage des KPI généraux pour fichier 1
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    display_metric_card("Fournisseurs", df1["Fournisseur"].nunique(), color="#4527A0")
                with col2:
                    display_metric_card("Bons de commande", df1["Bon de commande"].nunique(), color="#00897B")
                with col3:
                    display_metric_card("Matériels uniques", df1["Matériel"].nunique(), color="#C62828")
                with col4:
                    display_metric_card("Lignes de commande", df1.shape[0], color="#F9A825")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Style du tableau récapitulatif
                st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
                # Renommer les colonnes pour une meilleure présentation
                years_summary1 = years_summary1.rename(columns={
                    "Year": "Année", 
                    "nb_vendors": "Fournisseurs", 
                    "nb_orders": "Bons de commande",
                    "nb_materials": "Matériels uniques",
                    "nb_lignes": "Lignes de commande"
                })
                
                # Formater les nombres - sans virgule pour les années
                years_summary1["Année"] = years_summary1["Année"].apply(lambda x: format_number(x, is_year=True))
                
                # Formater les autres colonnes avec séparateurs de milliers
                for col in ["Fournisseurs", "Bons de commande", "Matériels uniques", "Lignes de commande"]:
                    years_summary1[col] = years_summary1[col].apply(lambda x: format_number(x))
                
                # Afficher le DataFrame sans l'index
                st.dataframe(years_summary1, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

                
                # Fichier 2
                st.markdown("<h4 style='color: #1E88E5; margin-top: 30px;'>Fichier 2: Commandes</h4>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="background-color: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 5px solid #4caf50; margin: 15px 0;">
                    <p style="margin: 0; color: #1b5e20;">✓ Base de données chargée avec succès: <b>{df2.shape[0]}</b> lignes et <b>{df2.shape[1]}</b> colonnes</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # Résumé pour le fichier 2
                years_summary2 = df2.groupby("Year").agg(
                    nb_vendors=("Fournisseur", "nunique"),
                    nb_orders=("Bons de commande", "nunique"),
                    nb_materials=("Matériel", "nunique"),
                    nb_lignes=("Matériel", "count"),
                    total_value=("Valeur nette de la commande", "sum")
                ).reset_index()
                
                st.markdown("<h5 style='color: #1E88E5; margin-top: 20px;'>Résumé</h5>", unsafe_allow_html=True)
                
                # Assurer que les métriques ont la même taille
                st.markdown('<div class="equal-height-cols">', unsafe_allow_html=True)
                # Affichage des KPI généraux pour fichier 2
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    display_metric_card("Fournisseurs", df2["Fournisseur"].nunique(), color="#4527A0")
                with col2:
                    display_metric_card("Bons de commande", df2["Bons de commande"].nunique(), color="#00897B")
                with col3:
                    display_metric_card("Matériels uniques", df2["Matériel"].nunique(), color="#C62828")
                with col4:
                    display_metric_card("Lignes de commande", df2.shape[0], color="#F9A825")
                with col5:
                    display_metric_card("Valeur totale", format_currency(df2["Valeur nette de la commande"].sum()), color="#6A1B9A")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Style du tableau récapitulatif
                st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
                # Renommer les colonnes pour une meilleure présentation
                years_summary2 = years_summary2.rename(columns={
                    "Year": "Année", 
                    "nb_vendors": "Fournisseurs", 
                    "nb_orders": "Bons de commande",
                    "nb_materials": "Matériels uniques",
                    "nb_lignes": "Lignes de commande",
                    "total_value": "Valeur totale"
                })
                
                # Formater les nombres - sans virgule pour les années
                years_summary2["Année"] = years_summary2["Année"].apply(lambda x: format_number(x, is_year=True))
                
                # Formater les autres colonnes avec séparateurs de milliers
                for col in ["Fournisseurs", "Bons de commande", "Matériels uniques", "Lignes de commande"]:
                    years_summary2[col] = years_summary2[col].apply(lambda x: format_number(x))
                
                # Formater la valeur totale
                years_summary2["Valeur totale"] = years_summary2["Valeur totale"].apply(format_currency)
                
                # Afficher le DataFrame sans l'index
                st.dataframe(years_summary2, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Instructions d'utilisation
                st.markdown(
                    """
                    <div style="background-color: #e3f2fd; padding: 20px; border-radius: 10px; margin-top: 30px;">
                    <h3 style="color: #1E88E5; margin-top: 0;">💡 Comment analyser les performances fournisseurs</h3>
                    <p>Utilisez les filtres dans la barre latérale pour explorer les deux ensembles de données en parallèle :</p>
                    <ul>
                      <li>Sélectionnez une <b>année</b> pour voir les délais de livraison et les commandes sur cette période</li>
                      <li>Choisissez un <b>mois</b> pour analyser les performances mensuelles et valeurs de commande</li>
                      <li>Utilisez le <b>menu déroulant</b> pour sélectionner un fournisseur spécifique</li>
                      <li>Sélectionnez une <b>gamme de produit</b> pour analyser les performances par gamme</li>
                      <li>Filtrez par <b>type VC</b> pour analyser séparément les produits VC et Non VC (sélection multiple possible)</li>
                    </ul>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )


if __name__ == "__main__":
    main()
