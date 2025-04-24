import streamlit as st
import pandas as pd
from utils.bd import load_annonces, load_modeles
from streamlit_extras.switch_page_button import switch_page

# === Configuration de la page ===
st.set_page_config(page_title="Détail de l’annonce", page_icon="📄", layout="wide")
st.title("📄 Détail de l’annonce")

# === Chargement des annonces ===
df = load_annonces()

annonce_id = st.session_state.get("annonce_id")
if annonce_id is None or annonce_id not in df.index:
    st.error("❌ Annonce non trouvée.")
    st.stop()

annonce = df.loc[annonce_id]

# === Affichage de l'annonce ===
st.image(annonce["url_image"], width=600)
st.header(f"{annonce['marque']} {annonce['modele']}")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**📅 Année :** {annonce['annee']}")
    prix = annonce.get("prix")
    st.markdown(f"**💰 Prix :** {int(prix)} CAD" if pd.notna(prix) else "**💰 Prix :** N/O")
    km = annonce.get("kilometrage")
    st.markdown(f"**🛣️ Kilométrage :** {int(km)} km" if pd.notna(km) else "**🛣️ Kilométrage :** N/O")
    st.markdown(f"**📍 Ville :** {annonce['ville']}")
    st.markdown(f"**🛠️ Transmission :** {annonce['transmission']}")
    st.markdown(f"**⛽ Carburant :** {annonce['carburant']}")

with col2:
    st.markdown(f"**🎨 Couleur extérieure :** {annonce.get('couleur', 'Non spécifiée')}")
    st.markdown(f"**🎨 Intérieur :** {annonce.get('couleur_interieure', 'Non spécifiée')}")
    st.markdown(f"**🧠 Moteur :** {annonce.get('moteur', 'Non spécifié')}")
    st.markdown(f"**🚗 Carrosserie :** {annonce.get('carrosserie', 'Non spécifiée')}")
    st.markdown(f"**📦 Plateforme :** {annonce.get('plateforme', 'Non spécifiée')}")

lien = annonce.get("lien", None)
if pd.notna(lien):
    st.markdown(f"[🔗 Voir l'annonce en ligne]({lien})")

# === Navigation ===
if st.button("⬅️ Retour aux annonces"):
    switch_page("annonces")

if st.button("⬅️ Retour aux analyses"):
    switch_page("analyse")

# === Modèles de référence ===
st.markdown("---")
# st.subheader("🔍 Modèles de référence similaire")

df_modeles = load_modeles()
# st.markdown(f"📊 **Nombre total de modèles dans la base :** {len(df_modeles)}")  # <= ici

if df_modeles.empty:
    st.warning("Aucune donnée dans la table des modèles.")
    
if df_modeles.empty:
    st.warning("Aucune donnée dans la table des modèles.")
else:
    # Extraction et nettoyage des champs
    marque = str(annonce.get("marque", "")).strip().lower()
    modele = str(annonce.get("modele", "")).strip().lower()
    annee = int(annonce.get("annee")) if pd.notna(annonce.get("annee")) else None

    df_modeles["marque_clean"] = df_modeles["marque"].astype(str).str.strip().str.lower()
    df_modeles["modele_clean"] = df_modeles["modele"].astype(str).str.strip().str.lower()
    df_modeles["annee_clean"] = pd.to_numeric(df_modeles["annee"], errors='coerce')

    filtres = (
        (df_modeles["marque_clean"] == marque) &
        (df_modeles["modele_clean"] == modele) &
        (df_modeles["annee_clean"] == annee)
    )

    modeles_similaires = df_modeles[filtres]

    # === DEBUG pour vérifier les valeurs ===
    # st.markdown("### 🧪 Données de référence complètes")
    # st.dataframe(df_modeles)

    # st.markdown("### 🧪 Valeurs utilisées pour le filtrage")
    # st.write(f"**Marque :** {marque}")
    # st.write(f"**Modèle :** {modele}")
    # st.write(f"**Année :** {annee}")

    # st.markdown("### 🧪 Filtrage uniquement par marque")
    # st.dataframe(df_modeles[df_modeles["marque_clean"] == marque])

    # st.markdown("### 🧪 Filtrage par marque + modèle")
    # st.dataframe(df_modeles[(df_modeles["marque_clean"] == marque) & (df_modeles["modele_clean"] == modele)])

    # st.markdown("### 🧪 Filtrage marque + modèle + année")
    # if modeles_similaires.empty:
    #     st.info("Aucun modèle de référence correspondant trouvé.")
    # else:
    #     st.dataframe(modeles_similaires)

# === Affichage du 1er modèle similaire ===
if not modeles_similaires.empty:
    st.subheader("🔍 Modèles de référence similaire")

    premier_modele = modeles_similaires.iloc[0]

    # Colonnes à exclure
    colonnes_ignorees = {"id_modele", "lien_modele", "marque_clean", "modele_clean", "annee_clean"}

    # Colonnes à afficher (filtrées)
    colonnes_a_afficher = [
        col for col in premier_modele.index
        if col not in colonnes_ignorees and pd.notna(premier_modele[col]) and str(premier_modele[col]).strip() != ""
    ]

    col1, col2 = st.columns(2)
    mi = len(colonnes_a_afficher) // 2

    with col1:
        for col in colonnes_a_afficher[:mi]:
            st.markdown(f"**{col.replace('_', ' ').capitalize()} :** {premier_modele[col]}")

    with col2:
        for col in colonnes_a_afficher[mi:]:
            st.markdown(f"**{col.replace('_', ' ').capitalize()} :** {premier_modele[col]}")
