import csv
import psycopg2

# === Connexion à la base PostgreSQL ===
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    dbname="Projet_auto",
    user="postgres",
    password="azerty"
)
cursor = conn.cursor()

# === Nettoyage de la table ===
try:
    cursor.execute("DELETE FROM Modele")
    conn.commit()
    print("🧹 Table 'Modele' vidée.")

    # Essai de réinitialiser la séquence si elle existe (facultatif)
    try:
        cursor.execute("ALTER SEQUENCE modele_id_seq RESTART WITH 1")
        conn.commit()
        print("🔁 Séquence 'modele_id_seq' réinitialisée.")
    except Exception as seq_err:
        print("⚠️ Séquence non réinitialisée (peut ne pas exister).")

except Exception as e:
    print(f"❌ Erreur lors du nettoyage de la table : {e}")
    conn.rollback()

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

# === Lecture du fichier CSV et insertion ===
inserted = 0
ignored = 0

with open("data_auto123_normalized.csv", mode="r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        annee = clean_str(row.get("annee"))
        marque = clean_str(row.get("marque"))
        modele = clean_str(row.get("modele"))
        prix = safe_float(row.get("prix"))
        moteur = clean_str(row.get("moteur"))
        transmission = clean_str(row.get("transmission"))
        portes = safe_int(row.get("portes"))
        consommation_modele = clean_str(row.get("consommation"))
        puissance_modele = safe_float(row.get("puissance"))
        carrosserie_modele = clean_str(row.get("carrosserie"))
        lien_modele = clean_str(row.get("url"))
        sous_modele = clean_str(row.get("sous_modele"))
        version_ = clean_str(row.get("version"))
        nombre_place = safe_int(row.get("places"))

        try:
            cursor.execute("""
                INSERT INTO Modele (
                    marque, modele, annee, sous_modele, version_, prix,
                    consommation_modele, moteur_modele, puissance_modele,
                    transmission_modele, carrosserie_modele, nombre_porte,
                    nombre_place, lien_modele
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                marque, modele, annee, sous_modele, version_, prix,
                consommation_modele, moteur, puissance_modele,
                transmission, carrosserie_modele, portes,
                nombre_place, lien_modele
            ))
            inserted += 1
        except Exception as e:
            print(f"❌ Erreur à la ligne {i} : {e}")
            conn.rollback()
            ignored += 1

# === Fin de la session ===
conn.commit()
cursor.close()
conn.close()

print(f"\n✅ Import terminé : {inserted} lignes insérées, {ignored} ignorées.")
