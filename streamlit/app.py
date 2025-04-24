import streamlit as st


st.set_page_config(
    page_title="AutoScoop - Accueil",
    page_icon="🚗",
    layout="centered"
)

st.markdown("<h1 style='text-align: center;'>🚗 AutoScoop</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Bienvenue sur la plateforme intelligente de vente de véhicules d'occasion</h3>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: justify; font-size: 18px; margin-top: 30px;">
AutoScoop regroupe en un seul endroit l’ensemble des annonces de véhicules d’occasion issues de différentes plateformes de vente en ligne. 
<br><br>
Grâce à notre technologie d’agrégation et d’analyse, nous vous offrons une **vision claire du marché** dans la grande région de **Montréal**, en mettant en lumière les tendances de prix, les modèles les plus populaires et bien plus encore.
<br><br>
Explorez dès maintenant :
- 📊 **Analyse du marché** pour visualiser les tendances
- 🔍 **Annonces filtrables** avec photos, prix et localisation
- 🧾 **Modèle de référence** pour comparer les véhicules
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align: center;'>🚀 Prêt à explorer ? Utilisez le menu à gauche pour naviguer !</div>", unsafe_allow_html=True)
