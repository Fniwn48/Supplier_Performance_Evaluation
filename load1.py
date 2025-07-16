import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


@st.cache_data
def merge_df(df1, df2):
    """
    Ajoute les colonnes 'Order Quantity' de df2 à df1 sans créer de lignes supplémentaires.
    Supprime les doublons après fusion pour garder exactement les mêmes lignes que df1.
    """
    if df1 is None or df2 is None or df1.empty or df2.empty:
        return df1
    
    # Sauvegarder le nombre de lignes initial
    initial_rows = len(df1)
    
    # Préparer df2 pour la fusion
    df2_prep = df2[["Bons de commande", "Fournisseur", "Matériel", "Date du document", "Order Quantity"]].rename(columns={
        "Bons de commande": "Bon de commande",
        "Date du document": "Document Date"
    }).reset_index(drop=True)
    
    # Fusion (peut créer des doublons)
    result = pd.merge(df1.reset_index(drop=True), df2_prep, on=["Bon de commande", "Fournisseur", "Matériel"], how="left")
    
    # Afficher combien de lignes ont été créées
    st.write(f"🔍 Lignes avant fusion : {initial_rows}")
    st.write(f"🔍 Lignes après fusion : {len(result)}")
    
    # Supprimer les doublons basés sur TOUTES les colonnes originales de df1
    # Identifier les colonnes de df1 (sans les nouvelles colonnes ajoutées)
    df1_columns = df1.columns.tolist()
    
    # Supprimer les doublons en gardant la première occurrence
    result_deduplicated = result.drop_duplicates(subset=df1_columns, keep='first')
    
    st.write(f"🔍 Lignes après suppression des doublons : {len(result_deduplicated)}")
    
    # Vérification finale
    if len(result_deduplicated) != initial_rows:
        st.warning(f"⚠️ Attention : {initial_rows} lignes attendues, {len(result_deduplicated)} lignes obtenues")
        
        # Afficher quelques exemples de doublons pour debug
        if len(result) > initial_rows:
            st.write("📋 Exemples de doublons détectés :")
            duplicates = result[result.duplicated(subset=df1_columns, keep=False)]
            st.dataframe(duplicates.head(10))
    
    return result_deduplicated
    
@st.cache_data
def add_vc_status(df, vc_file):
   """
   Ajoute la colonne 'Type VC' à un DataFrame en identifiant les matériaux VC.
   
   Args:
       df: DataFrame auquel ajouter la colonne 'Type VC'
       vc_file: Fichier Excel contenant la liste des matériaux VC
       
   Returns:
       DataFrame avec la colonne 'Type VC' ajoutée
   """
   if vc_file is None:
       return df
   
   try:
       # Vérifier que le DataFrame contient la colonne Matériel
       if "Matériel" not in df.columns:
           return df
       
       # Charger le fichier VC
       vc_df = pd.read_excel(vc_file)
       
       # Vérifier que le fichier VC contient la colonne Material
       if "Material" not in vc_df.columns:
           return df
       
       # Créer une liste des matériaux VC (unique)
       vc_materials = vc_df["Material"].unique().tolist()
       
       # Ajouter la colonne Type VC
       df["Type VC"] = df["Matériel"].apply(
           lambda x: "Install" if x == "Y5010646" else ("VC" if x in vc_materials else "Standard")
       )
       
       return df
       
   except Exception as e:
       return df

@st.cache_data
def add_prodline_name(df, reference_file):
    """
    Ajoute la colonne 'Prodline Name' à un DataFrame en utilisant un fichier de référence.
    Se base sur la correspondance exacte des trois colonnes: Fournisseur, Matériel, et Matériel du fournisseur.
    
    Args:
        df: DataFrame auquel ajouter la colonne 'Prodline Name'
        reference_file: Fichier Excel contenant les correspondances
        
    Returns:
        DataFrame avec la colonne 'Prodline Name' ajoutée
    """
    if reference_file is None:
        st.warning("Aucun fichier de référence pour Prodline Name n'a été fourni.")
        return df
    
    try:
        # Vérification des colonnes nécessaires dans le DataFrame d'entrée
        required_input_columns = ["Fournisseur", "Matériel", "Matériel du fournisseur"]
        missing_columns = [col for col in required_input_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Le DataFrame d'entrée ne contient pas les colonnes nécessaires: {', '.join(missing_columns)}")
            return df
        
        # Chargement du fichier de référence
        ref_df = pd.read_excel(reference_file)
        
        # Vérification des colonnes requises dans le fichier de référence
        required_ref_columns = ["Vendor", "Material", "Vendor Material Number", "Prodline Name","MRP Controller"]
        missing_ref_columns = [col for col in required_ref_columns if col not in ref_df.columns]
        
        if missing_ref_columns:
            st.error(f"Le fichier de référence ne contient pas les colonnes nécessaires: {', '.join(missing_ref_columns)}")
            return df
        
        # Renommer les colonnes du fichier de référence pour correspondre au format de nos DataFrames
        ref_df = ref_df.rename(columns={
            "Vendor": "Fournisseur",
            "Material": "Matériel",
            "Vendor Material Number": "Matériel du fournisseur"
        })
        
        # Création d'une copie du DataFrame pour éviter les modifications en place
        df_with_prodline = df.copy()
        
        # Méthode plus efficace utilisant merge
        # Sélection des colonnes nécessaires du fichier de référence
        ref_df_slim = ref_df[["Fournisseur", "Matériel", "Matériel du fournisseur", "Prodline Name","MRP Controller"]]
        
        # Fusion des DataFrames sur les trois colonnes clés
        df_with_prodline = pd.merge(
            df_with_prodline, 
            ref_df_slim,
            on=["Fournisseur", "Matériel", "Matériel du fournisseur"],
            how="left"
        )
        
        # Remplacement des valeurs NaN par une valeur par défaut
        df_with_prodline["Prodline Name"] = df_with_prodline["Prodline Name"].fillna("NA / Raw Material / Semi fini")
        
        # Ajout de la colonne Drop Status basée sur la valeur de MRP Controller
        df_with_prodline["Drop Statut"] = df_with_prodline["MRP Controller"].apply(
            lambda x: "Drop" if x == "M50" else "No drop"
        )
        return df_with_prodline
        
    except Exception as e:
        st.error(f"Erreur lors de l'ajout de Prodline Name: {str(e)}")
        return df

@st.cache_data
def load_and_validate_file1(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            required_columns = ["Purchase order", "Vendor", "Name 1", "Material", 
                                "Material Description", "Vendor Material Number", "Posting Date", 
                                "Actual Lead Time", "Planned Deliv. Time"]
            df = df[required_columns]
            # Check that all required columns exist
            if all(column in df.columns for column in required_columns):
                #Remplacer les valeurs None par des chaînes vides pour les trois colonnes spécifiées
                df["Vendor Material Number"] = df["Vendor Material Number"].fillna("")
                df["Material Description"] = df["Material Description"].fillna("")
                df["Name 1"] = df["Name 1"].fillna("")
                
                # Date conversion
                df["Posting Date"] = pd.to_datetime(df["Posting Date"], errors='coerce')
                
                # Remove rows with invalid dates
                df = df.dropna(subset=["Posting Date"])
                
                # Convert lead time columns to numeric, coercing errors to NaN
                df["Actual Lead Time"] = pd.to_numeric(df["Actual Lead Time"], errors='coerce')
                df["Planned Deliv. Time"] = pd.to_numeric(df["Planned Deliv. Time"], errors='coerce')
                
                # Drop rows where either lead time is NaN
                df = df.dropna(subset=["Actual Lead Time", "Planned Deliv. Time"])
                
                # Extract year, month and month name
                df["Year"] = df["Posting Date"].dt.year
                df["Month"] = df["Posting Date"].dt.month
                df["Month_Name"] = df["Posting Date"].dt.strftime('%B')
                
                # Rename columns to French
                df = df.rename(columns={
                    "Purchase order": "Bon de commande",
                    "Vendor": "Fournisseur",
                    "Name 1": "Nom du fournisseur",
                    "Material": "Matériel",
                    "Material Description": "Description du matériel",
                    "Vendor Material Number": "Matériel du fournisseur",
                    "Posting Date": "Date de comptabilisation",
                    "Actual Lead Time": "Délai réel",
                    "Planned Deliv. Time": "Délai théorique"
                })
                
                # Exclude 2022 data and material "Y4950100"
                df = df[(df["Year"] != 2022) & (df["Matériel"] != "Y4950100")]
                
                # Calculate performance metrics
                df["Écart de délai"] = df["Délai réel"] - df["Délai théorique"]
                
                # Define delivery status based on new categories
                def categorize_delay(days_diff):
                    if days_diff < 0:
                        return "En avance"
                    elif 0 <= days_diff <= 1:
                        return "À temps"
                    elif 2 <= days_diff <= 7:
                        return "Retard accepté"
                    else:  # 8 days or more
                        return "Long délai"
                
                df["Statut de livraison"] = df["Écart de délai"].apply(categorize_delay)

                colonne_df = ['Year','Month','Month_Name','Bon de commande','Fournisseur','Nom du fournisseur','Matériel','Description du matériel','Matériel du fournisseur','Date de comptabilisation','Délai réel','Délai théorique','Écart de délai','Statut de livraison']
                df = df[colonne_df]
                
                return df
            else:
                missing_columns = [col for col in required_columns if col not in df.columns]
                st.error(f"Le fichier Excel ne contient pas les colonnes nécessaires: {', '.join(missing_columns)}")
                return None
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier: {str(e)}")
            return None
    return None

@st.cache_data
def load_and_validate_file2(uploaded_file, reference_df=None):
    if uploaded_file is None:
        return None
        
    try:
        # Chargement du fichier
        df2 = pd.read_excel(uploaded_file)
        
        # Vérification des colonnes requises
        required_columns = ["Purchasing Document", "Vendor", "Material", "Document Date", "Net Order Value","Order Unit","Order Quantity"]
        missing_columns = [col for col in required_columns if col not in df2.columns]
        
        if missing_columns:
            st.error(f"Le fichier Excel ne contient pas les colonnes nécessaires: {', '.join(missing_columns)}")
            return None
        
        # Création d'un nouveau DataFrame pour éviter les problèmes de référence
        df2_processed = pd.DataFrame()
        
        # Copier uniquement les colonnes nécessaires
        df2_processed["Bons de commande"] = df2["Purchasing Document"]
        df2_processed["Fournisseur"] = df2["Vendor"]
        df2_processed["Matériel"] = df2["Material"]
        df2_processed["Date du document"] = pd.to_datetime(df2["Document Date"], errors='coerce')
        df2_processed["Valeur nette de la commande"] = pd.to_numeric(df2["Net Order Value"], errors='coerce')
        df2_processed["Order Quantity"] = pd.to_numeric(df2["Order Quantity"], errors='coerce')
        df2_processed["Order Unit"] = df2["Order Unit"]

        
        # Nettoyer les données
        df2_processed = df2_processed.dropna(subset=["Date du document", "Valeur nette de la commande"])
        
        # Ajouter les informations temporelles
        df2_processed["Year"] = df2_processed["Date du document"].dt.year
        df2_processed["Month"] = df2_processed["Date du document"].dt.month
        df2_processed["Month_Name"] = df2_processed["Date du document"].dt.strftime('%B')
        
        # Initialiser les colonnes supplémentaires
        df2_processed["Nom du fournisseur"] = "Fournisseur inconnu"
        df2_processed["Description du matériel"] = ""
        df2_processed["Matériel du fournisseur"] = ""
        
        # Ajouter les informations de référence si disponibles
        if reference_df is not None and not reference_df.empty:
            # Créer un dictionnaire explicite avec reset_index pour éviter les problèmes d'index
            vendor_df = reference_df[["Fournisseur", "Nom du fournisseur"]].drop_duplicates(subset=["Fournisseur"]).reset_index(drop=True)
            vendor_dict = dict(zip(vendor_df["Fournisseur"].tolist(), vendor_df["Nom du fournisseur"].tolist()))
            
            # Appliquer le dictionnaire sans utiliser map/merge
            for idx, row in df2_processed.iterrows():
                vendor_code = row["Fournisseur"]
                if vendor_code in vendor_dict:
                    df2_processed.at[idx, "Nom du fournisseur"] = vendor_dict[vendor_code]
            
            # Créer un dictionnaire pour les informations matérielles
            material_dict = {}
            ref_data = reference_df[["Fournisseur", "Matériel", "Description du matériel", "Matériel du fournisseur"]]
            ref_data = ref_data.reset_index(drop=True)  # Reset l'index pour éviter les doublons
            
            for _, row in ref_data.iterrows():
                key = (row["Fournisseur"], row["Matériel"])
                # Si la clé existe déjà, ne pas la remplacer (prendre la première occurrence)
                if key not in material_dict:
                    material_dict[key] = {
                        "Description": row["Description du matériel"],
                        "VendorMaterial": row["Matériel du fournisseur"]
                    }
            
            # Appliquer le dictionnaire matériel ligne par ligne
            for idx, row in df2_processed.iterrows():
                key = (row["Fournisseur"], row["Matériel"])
                if key in material_dict:
                    df2_processed.at[idx, "Description du matériel"] = material_dict[key]["Description"]
                    df2_processed.at[idx, "Matériel du fournisseur"] = material_dict[key]["VendorMaterial"]
        
        return df2_processed
        
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {str(e)}")
        return None
    
def display_header():
    st.markdown("""
        <h1 style="color:#2c3e50; font-size: 36px;">
            Évaluation de la Performance de Livraison des Fournisseurs
        </h1>
    """, unsafe_allow_html=True)
