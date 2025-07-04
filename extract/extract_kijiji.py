import os
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -------- CONFIGURATION --------
BASE_URL = "https://www.kijiji.ca"
LISTING_URL = BASE_URL + "/b-autos-camions/grand-montreal/page-{}/c174l80002?view=list"
DATA_DIR = "warehouse/html/kijiji"
ANNONCES_DIR = os.path.join(DATA_DIR, "annonces")
LIENS_PATH = os.path.join(DATA_DIR, "liens_annonces.txt")
LAST_PAGE_PATH = os.path.join(DATA_DIR, "last_page.txt")

os.makedirs(ANNONCES_DIR, exist_ok=True)

# -------- CONFIG SELENIUM --------
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# -------- PHASE 1 : EXTRACTION DES LIENS --------
def charger_liens_existants():
    if not os.path.exists(LIENS_PATH):
        return set()
    with open(LIENS_PATH, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def sauvegarder_liens(nouveaux_liens):
    with open(LIENS_PATH, "a", encoding="utf-8") as f:
        for lien in nouveaux_liens:
            f.write(lien + "\n")

def sauvegarder_page(page):
    with open(LAST_PAGE_PATH, "w") as f:
        f.write(str(page))

def charger_page():
    if os.path.exists(LAST_PAGE_PATH):
        with open(LAST_PAGE_PATH, "r") as f:
            try:
                return int(f.read().strip())
            except:
                return 1
    return 1

def phase_1_extract_links():
    print("[kijiji] Début de l'extraction des liens...")
    liens_existants = charger_liens_existants()
    page = charger_page()
    total_nouveaux = 0
    pages_vides = 0

    while True:
        url = LISTING_URL.format(page)
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            balises = soup.find_all("a", {"data-testid": "listing-link"})

            liens_page = set()
            for a in balises:
                href = a.get("href")
                if href and href.startswith("/v-"):
                    full_url = BASE_URL + href
                    if full_url not in liens_existants:
                        liens_page.add(full_url)

            if liens_page:
                sauvegarder_liens(liens_page)
                liens_existants.update(liens_page)
                print(f"{len(liens_page)} nouveaux liens trouvés sur la page {page}")
                total_nouveaux += len(liens_page)
                pages_vides = 0
            else:
                print(f"0 nouveau lien sur la page {page}")
                pages_vides += 1
                if pages_vides >= 2:
                    break

            page += 1
            sauvegarder_page(page)
            time.sleep(1.5)

            if page % 20 == 0:
                print("Pause de 1 minute pour éviter le blocage...")
                time.sleep(60)

        except Exception as e:
            print(f"[ERREUR] Interruption à la page {page} : {e}")
            break

    print(f"[kijiji] Total de nouveaux liens collectés : {total_nouveaux}")
    return total_nouveaux > 0

# -------- PHASE 2 : RÉCUPÉRATION HTML --------
def phase_2_download_html():
    print("[kijiji] Passage à l'extraction des fichiers HTML...")

    liens = []
    with open(LIENS_PATH, "r", encoding="utf-8") as f:
        liens = [line.strip() for line in f if line.strip()]

    fichiers_existants = os.listdir(ANNONCES_DIR)
    indices = []
    for f in fichiers_existants:
        if f.startswith("annonce_") and f.endswith(".html"):
            try:
                i = int(f.replace("annonce_", "").replace(".html", ""))
                indices.append(i)
            except:
                continue

    start_index = max(indices) + 1 if indices else 1
    print(f"[kijiji] Reprise à l'index {start_index}/{len(liens)}")

    for idx, lien in enumerate(liens[start_index - 1:], start=start_index):
        try:
            driver.get(lien)
            time.sleep(0.2)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.1)

            with open(os.path.join(ANNONCES_DIR, f"annonce_{idx:06d}.html"), "w", encoding="utf-8") as f:
                f.write(driver.page_source)

            print(f"[OK] Annonce sauvegardée : {idx}")

            if idx % 20 == 0:
                print("Pause de 1 minute pour éviter le blocage...")
                time.sleep(60)

        except Exception as e:
            print(f"[ERREUR] Interruption à l'annonce {idx}: {e}")

    print("[kijiji] Téléchargement HTML terminé.")
    driver.quit()

# -------- SCRIPT PRINCIPAL --------
if __name__ == "__main__":
    liens_extraits = phase_1_extract_links()
    if not liens_extraits:
        phase_2_download_html()
