import os
import pandas as pd
import time
import random
import re
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

CSV_DIR = "warehouse/csv/kijiji/raffraichissement"
HTML_DIR = "warehouse/html/kijiji"
STATE_PATH = os.path.join(CSV_DIR, "last_refresh_index.txt")
LINKS_PATH = os.path.join(HTML_DIR, "liens_annonces.txt")
TODAY_DATE = datetime.now().strftime("%Y-%m-%d")
CSV_REFRESHED_PATH = os.path.join(CSV_DIR, f"raffraichi_{TODAY_DATE}.csv")
SUMMARY_PATH = os.path.join(CSV_DIR, f"resume_rafraichissement_{TODAY_DATE}.txt")

def get_latest_raffraichi_csv():
    pattern = re.compile(r"raffraichi_(\d{4}-\d{2}-\d{2})\.csv")
    candidates = []
    for fname in os.listdir(CSV_DIR):
        match = pattern.match(fname)
        if match:
            date = datetime.strptime(match.group(1), "%Y-%m-%d")
            candidates.append((date, fname))
    if not candidates:
        raise FileNotFoundError("Aucun fichier raffraichi_<date>.csv trouvé.")
    return os.path.join(CSV_DIR, max(candidates)[1])

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)

def main():
    # Étape 1 : copier le fichier le plus récent vers le fichier du jour
    source_file = get_latest_raffraichi_csv()
    if not os.path.exists(CSV_REFRESHED_PATH):
        print(f"📄 Copie de {os.path.basename(source_file)} → {os.path.basename(CSV_REFRESHED_PATH)}")
        shutil.copy(source_file, CSV_REFRESHED_PATH)
    else:
        print(f"⚠️ Le fichier {CSV_REFRESHED_PATH} existe déjà, on le mettra à jour.")

    # Étape 2 : chargement du fichier
    df = pd.read_csv(CSV_REFRESHED_PATH)
    if "lien" not in df.columns:
        raise ValueError("Colonne 'lien' manquante dans le CSV.")

    liens = []
    if os.path.exists(LINKS_PATH):
        with open(LINKS_PATH, "r", encoding="utf-8") as f:
            liens = [line.strip() for line in f if line.strip()]

    df["ancien_prix"] = df.get("ancien_prix", None)  # ✅ laisser vide par défaut
    df["date_rafraichi"] = df.get("date_rafraichi", None)
    df["vendue"] = df.get("vendue", False)

    start_index = 0
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            try:
                start_index = int(f.read().strip())
            except:
                pass

    driver = setup_driver()
    resume = []
    total = 0

    print(f"\n🔄 Début du rafraîchissement à partir de l'index {start_index}\n")

    for idx in range(start_index, len(liens)):
        lien = liens[idx]
        print(f"[{idx}] Vérification → {lien}")
        matched = df[df["lien"] == lien]

        if matched.empty or df.at[matched.index[0], "vendue"] == True:
            continue

        row_index = matched.index[0]

        try:
            driver.get(lien)
            time.sleep(random.uniform(0.4, 0.6))
            prix_tag = driver.find_elements(By.XPATH, '//p[@data-testid="vip-price"]')

            # Mettre la date du jour sur chaque ligne traitée
            df.at[row_index, "date_rafraichi"] = TODAY_DATE

            if not prix_tag:
                df.at[row_index, "vendue"] = True
                df.at[row_index, "ancien_prix"] = None  # ✅ vide si vendu
                resume.append(f"[VENDU] {lien}")
                print(f"[VENDU] {lien}")
            else:
                nouveau_prix = prix_tag[0].text.strip().replace("$", "").replace(",", "").replace(".00", "")
                ancien_prix = str(df.at[row_index, "prix"]).strip().replace(".0", "")

                if ancien_prix != nouveau_prix:
                    df.at[row_index, "ancien_prix"] = ancien_prix if ancien_prix else None
                    df.at[row_index, "prix"] = nouveau_prix
                    resume.append(f"[MISE À JOUR] {lien} | Ancien: {ancien_prix} → Nouveau: {nouveau_prix}")
                    print(f"[MISE À JOUR] {lien} | Ancien: {ancien_prix} → Nouveau: {nouveau_prix}")
                else:
                    df.at[row_index, "ancien_prix"] = None  # ✅ vide si inchangé
                    print(f"[IDENTIQUE] {lien} | Prix: {ancien_prix}")

        except Exception as e:
            print(f"[ERREUR] {lien} → {e}")
            continue

        total += 1
        if total % 10 == 0:
            df.to_csv(CSV_REFRESHED_PATH, index=False, encoding="utf-8-sig")
            with open(STATE_PATH, "w") as f:
                f.write(str(idx + 1))
            print(f"💾 {total} lignes enregistrées dans {CSV_REFRESHED_PATH}...\n")

    df.to_csv(CSV_REFRESHED_PATH, index=False, encoding="utf-8-sig")
    with open(STATE_PATH, "w") as f:
        f.write(str(len(liens)))
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(resume))

    print(f"\n✅ Terminé : {total} lignes traitées.")
    print(f"📄 Résumé disponible dans {SUMMARY_PATH}")
    driver.quit()

if __name__ == "__main__":
    main()
