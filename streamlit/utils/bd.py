import pandas as pd
import psycopg2
import streamlit as st

# Connexion PostgreSQL (utilisée dans les fonctions suivantes)
def get_connection():
    return psycopg2.connect(
        dbname="Projet_auto",
        user="postgres",
        password="youssef",
        host="host.docker.internal",
        port="5432"
    )

# Chargement table annonce
@st.cache_data(ttl=600)
def load_annonces():
    try:
        conn = get_connection()
        df = pd.read_sql('SELECT * FROM "annonce"', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des annonces : {e}")
        return pd.DataFrame()

# Chargement table modele
@st.cache_data(ttl=600)
def load_modeles():
    try:
        conn = get_connection()
        df = pd.read_sql('SELECT * FROM "modele"', conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des modèles : {e}")
        return pd.DataFrame()
