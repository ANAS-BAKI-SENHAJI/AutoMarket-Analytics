from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import psycopg2

# === Connexion PostgreSQL ===
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "Projet_auto",
    "user": "postgres",
    "password": "youssef"
}

# 📁 Chemin du fichier CSV (doit être monté dans Docker si Airflow est containerisé)
CSV_PATH = "/opt/airflow/data/Modele_auto123/modele_reference_final_v4.csv"

# === Fonctions de nettoyage ===
def safe_int(val):
    try:
        return int(float(str(val).strip()))
    except:
        return None

def safe_float(val):
    try:
        return float(str(val).strip())
    except:
        return None

def clean_str(val):
    return val.strip() if isinstance(val, str) and val.strip() != "" else None

# === Fonction de chargement CSV → PostgreSQL ===
def load_modele_from_csv():
    inserted = 0
    ignored = 0

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                annee = clean_str(row.get("annee"))
                marque = clean_str(row.get("marque"))
                modele = clean_str(row.get("modele"))
                prix = safe_float(row.get("prix"))
                moteur = clean_str(row.get("moteur"))
                transmission = clean_str(row.get("transmission"))
                portes = safe_int(row.get("portes"))
                consommation = clean_str(row.get("consommation"))
                puissance = safe_float(row.get("puissance"))
                carrosserie = clean_str(row.get("carrosserie"))
                lien = clean_str(row.get("url"))
                sous_modele = clean_str(row.get("sous_modele"))
                version = clean_str(row.get("version"))
                places = safe_int(row.get("places"))

                # Insertion SQL
                try:
                    cursor.execute("""
                        INSERT INTO Modele (
                            marque, modele, annee, sous_modele, version_, prix,
                            consommation_modele, moteur_modele, puissance_modele,
                            transmission_modele, carrosserie_modele, nombre_porte,
                            nombre_place, lien_modele
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (marque, modele, annee, sous_modele, prix, version_)
                        DO NOTHING;
                    """, (
                        marque, modele, annee, sous_modele, version, prix,
                        consommation, moteur, puissance, transmission, carrosserie,
                        portes, places, lien
                    ))
                    inserted += 1
                except Exception as e:
                    print(f"❌ Erreur à la ligne {i} : {e}")
                    conn.rollback()
                    ignored += 1

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ Import terminé : {inserted} lignes insérées, {ignored} ignorées.")

    except Exception as e:
        print(f"❌ Connexion ou exécution échouée : {e}")

# === Définition du DAG ===
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="load_modele_reference_dag",
    default_args=default_args,
    schedule_interval="@once",  # à changer selon tes besoins
    catchup=False,
    tags=["csv", "modele", "auto"]
) as dag:

    tache_chargement_modele = PythonOperator(
        task_id="load_modele_from_csv",
        python_callable=load_modele_from_csv
    )

    tache_chargement_modele
