import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
from streamlit_extras.switch_page_button import switch_page
from utils.bd import load_annonces

# === Configuration de la page ===
st.set_page_config("Analyse", layout="wide")
st.title("📊 Analyse des annonces")

# === Chargement des données ===
df = load_annonces()
if df.empty:
    st.warning("Aucune donnée disponible.")
    st.stop()

# === SIDEBAR : Filtres dynamiques réorganisés ===
st.sidebar.header("🔍 Filtres")

# Fonction slider avec mémoire de session (version sûre)
def safe_slider_with_memory(label, key, min_val, max_val):
    if min_val == max_val:
        min_val = max(0, min_val - 1)

    default = st.session_state.get(key, (min_val, max_val))
    default = (
        max(min_val, min(default[0], max_val)),
        max(min_val, min(default[1], max_val))
    )

    return st.sidebar.slider(label, min_val, max_val, default, key=key)

# === 1. Ville ===
villes = sorted(df["ville"].dropna().unique())
filtre_ville = st.sidebar.multiselect("Ville", villes)
df_ville = df[df["ville"].isin(filtre_ville)] if filtre_ville else df

# === 2. Carrosserie ===
if "type_carrosserie" in df.columns:
    carrosseries = sorted(df_ville["type_carrosserie"].dropna().unique())
    filtre_carrosserie = st.sidebar.multiselect("Carrosserie", carrosseries)
    df_carrosserie = df_ville[df_ville["type_carrosserie"].isin(filtre_carrosserie)] if filtre_carrosserie else df_ville
else:
    df_carrosserie = df_ville

# === 3. Marque ===
marques = sorted(df_carrosserie["marque"].dropna().unique())
filtre_marque = st.sidebar.multiselect("Marque", marques)
df_marque = df_carrosserie[df_carrosserie["marque"].isin(filtre_marque)] if filtre_marque else df_carrosserie

# === 4. Modèle ===
modeles = sorted(df_marque["modele"].dropna().unique())
filtre_modele = st.sidebar.multiselect("Modèle", modeles)
df_modele = df_marque[df_marque["modele"].isin(filtre_modele)] if filtre_modele else df_marque

# === 5. Année ===
if "annee" in df_modele.columns:
    annees = sorted(df_modele["annee"].dropna().unique())
    filtre_annee = st.sidebar.multiselect("Année", annees)
    df_annee = df_modele[df_modele["annee"].isin(filtre_annee)] if filtre_annee else df_modele
else:
    df_annee = df_modele

# === 6. Kilométrage ===
if not df_annee.empty:
    km_min, km_max = int(df_annee["kilometrage"].min()), int(df_annee["kilometrage"].max())
    km_range = safe_slider_with_memory("Kilométrage", "filtre_km_range", km_min, km_max)
    df_km = df_annee[(df_annee["kilometrage"] >= km_range[0]) & (df_annee["kilometrage"] <= km_range[1])]
else:
    df_km = df_annee

# === 7. Prix ===
if not df_km.empty:
    prix_min, prix_max = int(df_km["prix"].min()), int(df_km["prix"].max())
    prix_range = safe_slider_with_memory("Prix", "filtre_prix_range", prix_min, prix_max)
    df_filtré = df_km[(df_km["prix"] >= prix_range[0]) & (df_km["prix"] <= prix_range[1])]
else:
    df_filtré = df_km

# === Aucune donnée
if df_filtré.empty:
    st.warning("Aucune annonce ne correspond aux filtres sélectionnés.")
    st.stop()

# === Sélecteur de mode de visualisation ===
col1, col2 = st.columns([1, 1])
with col1:
    view_count = st.button("📦 Visualisation par nombre d'annonces")
with col2:
    view_price = st.button("💰 Visualisation par prix moyen")
 
# === Visualisation : Annonces par ville ===
if view_count or (not view_count and not view_price):
    st.subheader("📍 Nombre d’annonces par ville")
    par_ville = df_filtré["ville"].value_counts().reset_index()
    par_ville.columns = ["ville", "count"]
    fig_ville = px.bar(par_ville, x="ville", y="count", title="Annonces par ville")
    click_ville = plotly_events(fig_ville)

    if click_ville:
        st.session_state["filtre_ville"] = click_ville[0]["x"]
        st.session_state.pop("filtre_marque", None)
        st.session_state.pop("filtre_modele", None)
        switch_page("annonces")

    # === Visualisation : Annonces par type de carrosserie ===
    st.subheader("📈 Nombre d’annonces par type de carrosserie")
    par_carrosserie = df_filtré["type_carrosserie"].value_counts().reset_index()
    par_carrosserie.columns = ["type_carrosserie", "count"]
    fig_carrosserie = px.bar(par_carrosserie, x="type_carrosserie", y="count", title="Annonces par type de carrosserie")
    click_marque = plotly_events(fig_carrosserie)

    if click_marque:
        st.session_state["filtre_marque"] = click_marque[0]["x"]
        st.session_state.pop("filtre_modele", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")
        
    # === Visualisation : Annonces par marque ===
    st.subheader("📈 Nombre d’annonces par marque")
    par_marque = df_filtré["marque"].value_counts().reset_index()
    par_marque.columns = ["marque", "count"]
    fig_marque = px.bar(par_marque, x="marque", y="count", title="Annonces par marque")
    click_marque = plotly_events(fig_marque)

    if click_marque:
        st.session_state["filtre_marque"] = click_marque[0]["x"]
        st.session_state.pop("filtre_modele", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")

    # === Visualisation : Annonces par modèle ===
    st.subheader("🚗 Nombre d’annonces par modèle")
    par_modele = df_filtré["modele"].value_counts().reset_index()
    par_modele.columns = ["modele", "count"]
    fig_modele = px.bar(par_modele, x="modele", y="count", title="Annonces par modèle")
    click_modele = plotly_events(fig_modele)

    if click_modele:
        st.session_state["filtre_modele"] = click_modele[0]["x"]
        st.session_state.pop("filtre_marque", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")

    # === Visualisation : Scatter Prix vs Kilométrage ===
    fig_scatter = px.scatter(
        df_filtré,
        x="kilometrage",
        y="prix",
        color=df_filtré["marque"].astype(str),
        hover_data=["modele", "ville", "prix", "kilometrage"],
        title="📈 Prix vs Kilométrage"
    )

    clicked = plotly_events(fig_scatter, click_event=True, override_height=600)

    if clicked:
        # 🔍 Extraction des coordonnées du point cliqué
        x_clicked = clicked[0]["x"]
        y_clicked = clicked[0]["y"]

        # 🔍 Match avec la ligne correspondante dans le df
        match = df[(df["kilometrage"] == x_clicked) & (df["prix"] == y_clicked)]

        if not match.empty:
            annonce_id = match.index[0]
            st.session_state["annonce_id"] = annonce_id
            st.success(f"✅ Redirection vers annonce ID {annonce_id}")
            switch_page("details")
        else:
            st.error("❌ Impossible d'associer ce point à une annonce.")

if view_price:
    # === Visualisation : Prix moyen par ville ===
    st.subheader("📍 Prix moyen par ville")
    par_ville = df_filtré.groupby("ville")["prix"].mean().reset_index()
    fig_ville = px.bar(par_ville, x="ville", y="prix", title="Prix moyen par ville")
    click_ville = plotly_events(fig_ville)

    if click_ville:
        st.session_state["filtre_ville"] = click_ville[0]["x"]
        st.session_state.pop("filtre_marque", None)
        st.session_state.pop("filtre_modele", None)
        switch_page("annonces")

    # === Visualisation : Prix moyen par type de carrosserie ===
    st.subheader("📈 Prix moyen par type de carrosserie")
    par_carrosserie = df_filtré.groupby("type_carrosserie")["prix"].mean().reset_index()
    fig_carrosserie = px.bar(par_carrosserie, x="type_carrosserie", y="prix", title="Prix moyen par type de carrosserie")
    click_marque = plotly_events(fig_carrosserie)

    if click_marque:
        st.session_state["filtre_marque"] = click_marque[0]["x"]
        st.session_state.pop("filtre_modele", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")

    # === Visualisation : Prix moyen par marque ===
    st.subheader("📈 Prix moyen par marque")
    par_marque = df_filtré.groupby("marque")["prix"].mean().reset_index()
    fig_marque = px.bar(par_marque, x="marque", y="prix", title="Prix moyen par marque")
    click_marque = plotly_events(fig_marque)

    if click_marque:
        st.session_state["filtre_marque"] = click_marque[0]["x"]
        st.session_state.pop("filtre_modele", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")

    # === Visualisation : Prix moyen par modèle ===
    st.subheader("🚗 Prix moyen par modèle")
    par_modele = df_filtré.groupby("modele")["prix"].mean().reset_index()
    fig_modele = px.bar(par_modele, x="modele", y="prix", title="Prix moyen par modèle")
    click_modele = plotly_events(fig_modele)

    if click_modele:
        st.session_state["filtre_modele"] = click_modele[0]["x"]
        st.session_state.pop("filtre_marque", None)
        st.session_state.pop("filtre_ville", None)
        switch_page("annonces")

    # === Visualisation : Scatter Prix vs Kilométrage ===
    fig_scatter = px.scatter(
        df_filtré,
        x="kilometrage",
        y="prix",
        color=df_filtré["marque"].astype(str),
        hover_data=["modele", "ville", "prix", "kilometrage"],
        title="📉 Prix vs Kilométrage"
    )

    clicked = plotly_events(fig_scatter, click_event=True, override_height=600)

    if clicked:
        x_clicked = clicked[0]["x"]
        y_clicked = clicked[0]["y"]
        match = df[(df["kilometrage"] == x_clicked) & (df["prix"] == y_clicked)]
        if not match.empty:
            annonce_id = match.index[0]
            st.session_state["annonce_id"] = annonce_id
            st.success(f"✅ Redirection vers annonce ID {annonce_id}")
            switch_page("details")
        else:
            st.error("❌ Impossible d'associer ce point à une annonce.")
