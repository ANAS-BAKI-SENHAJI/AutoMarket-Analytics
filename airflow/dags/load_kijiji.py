from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import psycopg2

# === Paramètres PostgreSQL ===
DB_CONFIG = {
    "host": "db",  
    "port": "5432",
    "dbname": "Projet_auto",
    "user": "postgres",
    "password": "youssef"
}

# 📁 Chemin du fichier CSV dans le container Docker
CSV_PATH = "/opt/airflow/data/kijiji/annonces_kijiji.csv"

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

# === Fonction principale d'insertion CSV → PostgreSQL ===
def load_kijiji_csv():
    inserted = 0
    ignored = 0

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                annee = safe_int(row.get("annee"))
                marque = clean_str(row.get("marque"))
                modele = clean_str(row.get("modele"))
                prix = safe_float(row.get("prix"))

                if None in (annee, marque, modele, prix):
                    print(f"🔁 Ligne {i} ignorée : {row}")
                    ignored += 1
                    continue

                try:
                    cursor.execute("""
                        INSERT INTO Annonce (
                            Annee, Marque, Modele, Prix, Kilometrage, Ville, lien_annonce,
                            type_carrosserie, couleur_exterieure, couleur_interieure,
                            transmission, carburant, nombre_place, nombre_porte,
                            equipements, url_image, plateforme
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        annee,
                        marque,
                        modele,
                        prix,
                        safe_int(row.get("kilometrage")),
                        clean_str(row.get("ville")),
                        clean_str(row.get("lien")),
                        clean_str(row.get("carrosserie")),
                        clean_str(row.get("couleur")),
                        clean_str(row.get("couleur_interieure")),
                        clean_str(row.get("transmission")),
                        clean_str(row.get("type_carburant")),
                        clean_str(row.get("nombre_places")),
                        safe_int(row.get("nombre_portes")),
                        clean_str(row.get("equipements")),
                        clean_str(row.get("URL_image")),
                        clean_str(row.get("plateforme"))
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
        print(f"❌ Erreur de connexion ou de traitement : {e}")

# === Définition du DAG Airflow ===
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="load_kijiji_annonces_dag",
    default_args=default_args,
    schedule_interval="@once",  # ou @daily selon besoin
    catchup=False,
    tags=["kijiji", "csv", "annonce"]
) as dag:

    task_load_kijiji = PythonOperator(
        task_id="load_annonces_kijiji_from_csv",
        python_callable=load_kijiji_csv
    )

    task_load_kijiji
