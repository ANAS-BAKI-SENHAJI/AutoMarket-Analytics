import os
import glob
import pandas as pd
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

HTML_DIR = "warehouse/html/kijiji/annonces"
CSV_DIR = "warehouse/csv/kijiji/raffraichissement"
DATE_TODAY = datetime.now().strftime("%Y-%m-%d")
CSV_NEW_PATH = os.path.join(CSV_DIR, f"nouvelles_annonces_{DATE_TODAY}.csv")
CSV_FINAL_PATH = os.path.join(CSV_DIR, f"raffraichi_{DATE_TODAY}.csv")
STATE_PATH = os.path.join(CSV_DIR, "last_transformed.txt")

DOUBLE_WORD_MAKES = ["Land Rover", "Rolls Royce", "Alfa Romeo", "Aston Martin", "Mini Cooper"]

def get_latest_raffraichi_csv():
    pattern = re.compile(r"raffraichi_(\d{4}-\d{2}-\d{2})\.csv")
    candidates = []
    for fname in os.listdir(CSV_DIR):
        match = pattern.match(fname)
        if match:
            date = datetime.strptime(match.group(1), "%Y-%m-%d")
            candidates.append((date, fname))
    if not candidates:
        return None
    return os.path.join(CSV_DIR, max(candidates)[1])

def extract_year_make_model(text):
    words = text.strip().split()
    if len(words) < 2:
        return None, None, None
    year = words[0]
    if len(words) >= 3:
        maybe_make = f"{words[1]} {words[2]}"
        if maybe_make in DOUBLE_WORD_MAKES:
            return year, maybe_make, " ".join(words[3:])
    return year, words[1], " ".join(words[2:])

def extract_city(soup):
    try:
        tag = soup.find("p", class_="sc-578235a5-0 hLtuc sc-b6b338a8-5 tDsgS")
        return tag.text.strip() if tag else None
    except:
        return None

def extract_link(soup):
    scripts = soup.find_all("script", type="application/ld+json")
    for tag in scripts:
        try:
            j = json.loads(tag.string.strip())
            if isinstance(j, dict) and j.get("@type") == "Car":
                return j.get("url")
        except:
            continue
    return None

def clean_text(value, remove_keywords=None):
    if not value:
        return None
    if remove_keywords:
        for word in remove_keywords:
            value = re.sub(rf"\b{word}\b", "", value, flags=re.IGNORECASE)
    return value.strip().split(",")[0].split()[0]

def transform_new_files():
    os.makedirs(CSV_DIR, exist_ok=True)
    html_files = sorted(glob.glob(os.path.join(HTML_DIR, "*.html")))

    start_index = 0
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            try:
                start_index = int(f.read().strip())
            except:
                pass

    html_files = html_files[start_index:]
    print(f"Traitement à partir de l’index {start_index}...")

    data = []
    total = 0

    for idx, file in enumerate(html_files, start=start_index):
        try:
            with open(file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            item = {}

            block = soup.find("p", string=re.compile(r"\d{4}\s+\w+"))
            if not block:
                continue
            year, make, model = extract_year_make_model(block.text.strip())
            if not all([year, make, model]):
                continue

            item.update({
                "annee": year,
                "marque": make,
                "modele": model,
                "ville": extract_city(soup),
                "lien": extract_link(soup),
                "prix": None,
                "kilometrage": None,
                "URL_image": None,
                "carrosserie": None,
                "couleur": None,
                "couleur_interieure": None,
                "transmission": None,
                "type_carburant": None,
                "nombre_places": None,
                "nombre_portes": None,
                "equipements": None,
                "plateforme": "kijiji",
                "vendue": False,
                "date_rafraichi": DATE_TODAY,
                "ancien_prix": "N/A"
            })

            if not item["lien"]:
                continue

            price_tag = soup.find("p", {"data-testid": "vip-price"})
            if price_tag:
                item["prix"] = price_tag.text.strip().replace("$", "").replace(",", "").replace(".00", "")

            img_tag = soup.find("img", {"data-testid": "gallery-main-image"})
            if img_tag:
                item["URL_image"] = img_tag["src"]

            groups = soup.find_all("div", attrs={"data-testid": re.compile(r"vip-attributes-group.*")})
            for group in groups:
                for row in group.find_all("div"):
                    label = row.find("p", class_="sc-9d9a3b6-0 fAJNmV")
                    values = row.find_all("p", class_="sc-578235a5-0 hsLMPB")
                    if not (label and values):
                        continue
                    name = label.text.strip()
                    val = values[0].text.strip()
                    if name == "Kilometres":
                        item["kilometrage"] = val.replace(",", "")
                    elif name == "Transmission":
                        item["transmission"] = val
                    elif name == "Fuel":
                        item["type_carburant"] = val
                    elif name == "Seats":
                        item["nombre_places"] = re.sub(r"\D", "", val)
                    elif name == "Body Style":
                        item["carrosserie"] = val
                        if len(values) > 1:
                            item["nombre_portes"] = re.sub(r"\D", "", values[1].text.strip())
                    elif name == "Colour":
                        if len(values) >= 2:
                            item["couleur"] = clean_text(values[0].text.strip(), ["exterior"])
                            item["couleur_interieure"] = clean_text(values[1].text.strip(), ["interior"])
                        elif len(values) == 1:
                            item["couleur"] = clean_text(values[0].text.strip(), ["exterior"])

            features = soup.select("div.sc-eb45309b-0.dfPPWl span")
            item["equipements"] = ", ".join(ft.text.strip() for ft in features)

            data.append(item)
            total += 1

            if total % 10 == 0:
                df = pd.DataFrame(data)
                df.dropna(subset=["annee", "marque", "modele", "lien"], inplace=True)
                df.to_csv(CSV_NEW_PATH, mode="a", index=False, encoding="utf-8-sig", header=not os.path.exists(CSV_NEW_PATH))
                with open(STATE_PATH, "w") as f:
                    f.write(str(idx + 1))
                print(f"→ {total} annonces transformées jusqu’à l’index {idx}")
                data = []

        except Exception as e:
            print(f"Ignoré {file} : {e}")
            continue

    if data:
        df = pd.DataFrame(data)
        df.dropna(subset=["annee", "marque", "modele", "lien"], inplace=True)
        df.to_csv(CSV_NEW_PATH, mode="a", index=False, encoding="utf-8-sig", header=not os.path.exists(CSV_NEW_PATH))
        with open(STATE_PATH, "w") as f:
            f.write(str(start_index + total))

    print(f"\n✅ {total} nouvelles annonces transformées → {CSV_NEW_PATH}")

    # === PHASE 2 – Fusion avec les annonces déjà existantes
    latest = get_latest_raffraichi_csv()
    if os.path.exists(CSV_NEW_PATH):
        df_new = pd.read_csv(CSV_NEW_PATH)
        df_base = pd.read_csv(latest) if latest else pd.DataFrame()

        # Harmonisation des colonnes
        for col in df_new.columns:
            if col not in df_base.columns:
                df_base[col] = None
        for col in df_base.columns:
            if col not in df_new.columns:
                df_new[col] = None
        df_base = df_base[df_new.columns]  # réordonner selon df_new

        # Concaténation avec insertion à la fin
        df_merged = pd.concat([df_base, df_new], ignore_index=True)

        # ✅ Supprimer les doublons de lien en gardant la première occurrence
        df_merged.drop_duplicates(subset="lien", keep="first", inplace=True)

        # Sauvegarde finale
        df_merged.to_csv(CSV_FINAL_PATH, index=False, encoding="utf-8-sig")
        print(f"\n🔁 Fusion terminée (sans doublons) → {CSV_FINAL_PATH}")

if __name__ == "__main__":
    transform_new_files()
