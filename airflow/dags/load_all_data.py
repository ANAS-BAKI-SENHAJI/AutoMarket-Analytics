from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import csv
import os
import psycopg2

DB_CONFIG = {
    "host": "db",  
    "port": "5432",
    "dbname": "Projet_auto",
    "user": "postgres",
    "password": "youssef"
}

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

def safe_bool(val):
    if isinstance(val, str):
        val = val.strip().lower()
        return val in ["1", "true", "oui", "yes"]
    return bool(val)

def safe_date(val):
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d")
    except:
        return None

def clean_str(val):
    return val.strip() if isinstance(val, str) and val.strip() != "" else None

def get_csv_path():
    date_str = datetime.today().strftime("%Y-%m-%d")
    return f"/opt/airflow/data/kijiji/raffraichi_{date_str}.csv"

# === Fonction générique CSV → DB ===
def load_annonces_from_csv(source_name, csv_path):
    inserted = 0
    ignored = 0

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, 1):
                annee = safe_int(row.get("annee"))
                marque = clean_str(row.get("marque"))
                modele = clean_str(row.get("modele"))
                prix = safe_float(row.get("prix"))

                if None in (annee, marque, modele, prix):
                    ignored += 1
                    continue

                try:
                    cursor.execute("""
                            INSERT INTO Annonce (
                                annee, marque, modele, prix, kilometrage, ville, lien_annonce,
                                type_carrosserie, couleur_exterieure, couleur_interieure,
                                transmission, moteur, carburant, url_image, plateforme,
                                vendue, date_raffraichie, ancien_prix
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            ON CONFLICT (marque, modele, annee, kilometrage, prix, ville, plateforme)
                            DO NOTHING;
                        """, (
                            safe_int(row.get("annee")),
                            clean_str(row.get("marque")),
                            clean_str(row.get("modele")),
                            safe_float(row.get("prix")),
                            safe_int(row.get("kilometrage")),
                            clean_str(row.get("ville")),
                            clean_str(row.get("lien")),
                            clean_str(row.get("carrosserie")),
                            clean_str(row.get("couleur")),
                            clean_str(row.get("couleur_interieure")),
                            clean_str(row.get("transmission")),
                            clean_str(row.get("moteur")),
                            clean_str(row.get("type_carburant")),
                            clean_str(row.get("URL_image")),
                            clean_str(row.get("plateforme")),
                            safe_bool(row.get("vendue")),
                            safe_date(row.get("date_rafraichi")),
                            safe_float(row.get("ancien_prix"))
                        ))
                    inserted += 1
                except Exception as e:
                    conn.rollback()
                    ignored += 1

        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {source_name.upper()} : {inserted} insérées, {ignored} ignorées.")
    except Exception as e:
        print(f"❌ Connexion échouée : {e}")

# === Wrappers pour Airflow ===
def load_autohebdo():
    load_annonces_from_csv("autohebdo", "/opt/airflow/data/AutoHebdo/annonces_autohebdo2.csv")

def load_kijiji():
    load_annonces_from_csv("kijiji", get_csv_path())

    if not os.path.exists(get_csv_path()):
        print(f"❌ Fichier {get_csv_path()} introuvable.")
        return
    print(f"✅ Fichier {get_csv_path()} trouvé.")

# === DAG Definition ===
default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="import_annonces_csv_dag",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    tags=["csv", "annonces"]
) as dag:

    task_autohebdo = PythonOperator(
        task_id="import_autohebdo",
        python_callable=load_autohebdo
    )

    task_kijiji = PythonOperator(
        task_id="import_kijiji",
        python_callable=load_kijiji
    )

    # Choix : enchaîné ou parallèle
    task_autohebdo >> task_kijiji   # Séquentiel (autohebdo avant kijiji)
    # OU : exécuter en parallèle (décommente si souhaité)
    # [task_autohebdo, task_kijiji]
