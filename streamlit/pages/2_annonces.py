# === 📦 Imports ===
import streamlit as st
import pandas as pd
import math
from utils.bd import load_annonces
from streamlit_extras.switch_page_button import switch_page

# === ⚙️ Configuration de la page ===
st.set_page_config(page_title="Annonces", page_icon="🚗", layout="wide")
st.title("🚗 Annonces AutoScoop")

# === 📄 Chargement des données ===
df = load_annonces()
if df.empty:
    st.warning("Aucune donnée à afficher.")
    st.stop()

# === 🔁 Fonction utilitaire : remise à zéro de la pagination
def reset_page():
    st.session_state.page = 1

# === 🔍 Filtres dynamiques dans la sidebar ===
st.sidebar.header("🔍 Filtres")

# --- 📌 Marque : chargement des marques disponibles
marque = sorted(df["marque"].dropna().unique())

# --- 🔁 Récupération de la valeur de filtre dans session_state
val_marque = st.session_state.get("filtre_marque", marque)
if isinstance(val_marque, str):
    val_marque = [val_marque]

# --- ✅ Multiselect pour marque (discret, contrôlé par key uniquement)
selected_marque = st.sidebar.multiselect(
    "Marques",
    options=marque,
    key="filtre_marque",
    on_change=reset_page,
    label_visibility="collapsed",
    placeholder="Filtrer par marque..."
)

# --- 📌 Modèle : dépend des marques sélectionnées
# df_modele_filtré = df[df["marque"].isin(selected_marque)] if selected_marque else df
if selected_marque:
    if isinstance(selected_marque, str):
        selected_marque = [selected_marque]
    df_modele_filtré = df[df["marque"].isin(selected_marque)]
else:
    df_modele_filtré = df

modele = sorted(df_modele_filtré["modele"].dropna().unique())

val_modele = st.session_state.get("filtre_modele", marque)
if isinstance(val_modele, str):
    val_modele = [val_modele]

# --- ✅ Multiselect pour modèle (filtré dynamiquement par marque)
selected_modele = st.sidebar.multiselect(
    "Modeles",
    options=modele,
    key="filtre_modele",
    on_change=reset_page,
    label_visibility="collapsed",
    placeholder="Filtrer par modele..."
)

# --- 📌 Ville : chargement des marques disponibles
ville = sorted(df["ville"].dropna().unique())

# --- 🔁 Récupération de la valeur de filtre dans session_state
val_ville = st.session_state.get("filtre_ville", ville)
if isinstance(val_ville, str):
    val_ville = [val_ville]

# --- ✅ Multiselect pour marque (discret, contrôlé par key uniquement)
selected_ville = st.sidebar.multiselect(
    "Villes",
    options=ville,
    key="filtre_ville",
    on_change=reset_page,
    label_visibility="collapsed",
    placeholder="Filtrer par ville..."
)

# --- 📅 Année : sélection par multiselect (optionnel)
if "annee" in df.columns:
    annee = sorted(df["annee"].dropna().unique())
    selected_annee = st.sidebar.multiselect(
        "Années",
        options=annee,
        key="filtre_annee",
        on_change=reset_page,
        label_visibility="collapsed",
        placeholder="Filtrer par année..."
    )
else:
    selected_annee = []

# --- 🛣️ Kilométrage : sélection par plage (slider)
if not df.empty:
    km_min, km_max = int(df["kilometrage"].min()), int(df["kilometrage"].max())
    km_range = st.sidebar.slider(
        "Kilométrage",
        min_value=km_min,
        max_value=km_max,
        value=(km_min, km_max),
        key="filtre_km",
        on_change=reset_page
    )
else:
    km_range = (0, 0)

# === 🧼 Application des filtres
filtered_df = df.copy()
if isinstance(selected_ville, str):
    selected_ville = [selected_ville]
if selected_ville:
    filtered_df = filtered_df[filtered_df["ville"].isin(selected_ville)]

if isinstance(selected_marque, str):
    selected_marque = [selected_marque]
if selected_marque:
    filtered_df = filtered_df[filtered_df["marque"].isin(selected_marque)]

if isinstance(selected_modele, str):
    selected_modele = [selected_modele]
if selected_modele:
    filtered_df = filtered_df[filtered_df["modele"].isin(selected_modele)]

if "selected_annee" in locals() and selected_annee:
    filtered_df = filtered_df[filtered_df["annee"].isin(selected_annee)]

if km_range and len(km_range) == 2:
    filtered_df = filtered_df[
        (filtered_df["kilometrage"] >= km_range[0]) &
        (filtered_df["kilometrage"] <= km_range[1])
    ]

# === ⚠️ Avertissement si aucun résultat
if filtered_df.empty:
    st.warning("Aucune annonce ne correspond à vos critères.")
    st.stop()

# === 📄 Pagination ===
annonces_par_page = 12
nb_total = len(filtered_df)
nb_pages = max(1, math.ceil(nb_total / annonces_par_page))

if "page" not in st.session_state:
    st.session_state.page = 1

# --- 🔁 Contrôles de pagination
def pagination_controls(key_prefix="nav"):
    page = st.session_state.get("page", 1)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if page > 1:
            if st.button("◀️ Précédent", key=f"{key_prefix}_prev"):
                st.session_state.page = page - 1
                st.rerun()
    with col3:
        if page < nb_pages:
            if st.button("Suivant ▶️", key=f"{key_prefix}_next"):
                st.session_state.page = page + 1
                st.rerun()
    with col2:
        st.markdown(f"<div style='text-align: center;'>Page {page} sur {nb_pages}</div>", unsafe_allow_html=True)

# --- ⬆️ Pagination en haut de la page
pagination_controls("nav_top")

# === 📑 Découpage des annonces pour la page courante
start = (st.session_state.page - 1) * annonces_par_page
end = start + annonces_par_page
df_page = filtered_df.iloc[start:end]

# === 🖼️ Affichage des cartes d’annonces
for i in range(0, len(df_page), 3):
    cols = st.columns(3)
    rows = df_page.iloc[i:i+3]

    for col, (index, row) in zip(cols, rows.iterrows()):
        with col:
            with st.container(border=True):
                # 📸 Image de l'annonce
                if pd.notna(row.get("url_image", None)):
                    st.image(row["url_image"], use_container_width=True)

                # 📄 Infos principales de l'annonce
                st.subheader(f"{row['marque']} {row['modele']}")
                
                prix = row["prix"]
                prix_str = f"{int(prix)} prix" if pd.notna(prix) else "N/O"
                st.markdown(f"**Prix :** {prix_str}")

                km = row["kilometrage"]
                km_str = f"{int(km)} km" if pd.notna(km) else "N/O"
                st.markdown(f"**Kilométrage :** {km_str}")

                st.markdown(f"**Ville :** {row['ville']}")

                # 🔘 Bouton vers la fiche détaillée
                if st.button("Voir les détails", key=f"btn_{index}"):
                    st.session_state["annonce_id"] = index
                    switch_page("details")

# --- ⬇️ Pagination en bas de page
st.markdown("---")
pagination_controls("nav_bottom")
