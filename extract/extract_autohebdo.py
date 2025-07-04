import os
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Configuration du navigateur
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

# Lancer WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Paramètres
BASE_URL = "https://www.autohebdo.net/autos/qc/montreal/?rcp=100&rcs={}&srt=35&prx=250&prv=Québec&loc=H2K%204J4&hprc=True&wcp=True&sts=Neuf-Occasion&inMarket=advancedSearch"
LISTING_DIR = "warehouse/html/autohebdo"
ANNONCE_DIR = os.path.join(LISTING_DIR, "annonces")
LIENS_PATH = os.path.join(LISTING_DIR, "liens_annonces.txt")
LAST_PAGE_PATH = os.path.join(LISTING_DIR, "last_page.txt")

os.makedirs(ANNONCE_DIR, exist_ok=True)

# Lire les liens déjà extraits
existing_links = set()
if os.path.exists(LIENS_PATH):
    with open(LIENS_PATH, "r", encoding="utf-8") as f:
        existing_links = set(line.strip() for line in f if line.strip())

print(f"{len(existing_links)} liens déjà présents dans le fichier.")

# Reprendre à partir de la dernière page enregistrée
start_page = 0
if os.path.exists(LAST_PAGE_PATH):
    with open(LAST_PAGE_PATH, "r", encoding="utf-8") as f:
        try:
            start_page = int(f.read().strip())
        except:
            pass

print(f"Reprise du ratissage à partir de la page {start_page + 1}.")

# Phase 1 : Récupération des liens d'annonces
page = start_page
no_new_link_streak = 0
MAX_NO_NEW_PAGES = 2

while True:
    offset = page * 100
    url = BASE_URL.format(offset)
    print(f"\nChargement page {page + 1} : {url}")
    try:
        driver.get(url)
    except Exception as e:
        print(f"Erreur de connexion sur la page {page + 1}: {e}")
        break

    time.sleep(0.1)
    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.1)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    annonce_blocks = soup.select("div.result-item-inner")

    urls = []
    for block in annonce_blocks:
        a_tag = block.find("a", class_="inner-link", href=True)
        if a_tag:
            full_url = "https://www.autohebdo.net" + a_tag["href"]
            if full_url not in existing_links:
                urls.append(full_url)
                existing_links.add(full_url)

    print(f"{len(urls)} nouveaux liens détectés sur la page {page + 1}.")

    if urls:
        with open(LIENS_PATH, "a", encoding="utf-8") as f:
            for url in urls:
                f.write(url + "\n")
        no_new_link_streak = 0
    else:
        print("Aucun nouveau lien détecté sur cette page.")
        no_new_link_streak += 1
        if no_new_link_streak >= MAX_NO_NEW_PAGES:
            print(f"Fin automatique après {MAX_NO_NEW_PAGES} pages sans nouveau lien.")
            break

    with open(LAST_PAGE_PATH, "w", encoding="utf-8") as f:
        f.write(str(page + 1))

    page += 1
    time.sleep(0.1)

    if page % 20 == 0:
        print(f"Pause de 2 minutes après {page} pages...")
        time.sleep(120)

# Phase 2 : Téléchargement des pages HTML des annonces
print("\nDébut du ratissage des pages d'annonces...")
existing_html_files = os.listdir(ANNONCE_DIR)
existing_indices = []

for filename in existing_html_files:
    if filename.startswith("annonce_") and filename.endswith(".html"):
        try:
            num = int(filename.replace("annonce_", "").replace(".html", ""))
            existing_indices.append(num)
        except ValueError:
            continue

start_index = max(existing_indices) + 1 if existing_indices else 1
print(f"Reprise à partir de l'annonce {start_index}")

with open(LIENS_PATH, "r", encoding="utf-8") as f:
    all_links = [line.strip() for line in f if line.strip()]

for idx, link in enumerate(all_links[start_index - 1:], start=start_index):
    try:
        driver.get(link)
        time.sleep(0.2)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)

        path = os.path.join(ANNONCE_DIR, f"annonce_{idx:06d}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print(f"Annonce {idx} sauvegardée.")

        if idx % 20 == 0:
            print(f"Pause de 1 minute après {idx} annonces...")
            time.sleep(60)

    except Exception as e:
        print(f"Erreur sur {link} : {e}")
        continue

print("\nRatissage des annonces terminé.")
driver.quit()
