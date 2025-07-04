import os
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

# Chemins
BASE_URL = "https://www.kijiji.ca"
LISTING_URL = "https://www.kijiji.ca/b-autos-et-camions/ville-de-montreal/page-{}/c174l1700281?sort=dateDesc"
LIENS_PATH = "warehouse/html/kijiji/liens_annonces.txt"
LAST_PAGE_PATH = "warehouse/html/kijiji/last_page.txt"
LAST_SCRAPE_DATE_PATH = "warehouse/html/kijiji/last_scrape_date.txt"
LAST_HTML_INDEX_PATH = "warehouse/html/kijiji/last_html_index.txt"
WAREHOUSE_PATH = "warehouse/html/kijiji/annonces"

def get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def reset_scrape_state_if_needed():
    today = get_today_str()
    if os.path.exists(LAST_SCRAPE_DATE_PATH):
        with open(LAST_SCRAPE_DATE_PATH, "r") as f:
            last_date = f.read().strip()
        if last_date != today:
            with open(LAST_PAGE_PATH, "w") as f:
                f.write("1")
            print("Nouveau jour détecté : on recommence à la page 1")
    with open(LAST_SCRAPE_DATE_PATH, "w") as f:
        f.write(today)

def get_start_page():
    if os.path.exists(LAST_PAGE_PATH):
        try:
            with open(LAST_PAGE_PATH, "r") as f:
                return int(f.read().strip())
        except:
            return 1
    return 1

def read_existing_links():
    if os.path.exists(LIENS_PATH):
        with open(LIENS_PATH, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def get_links_from_page(driver):
    time.sleep(random.uniform(0.6, 0.8))
    elements = driver.find_elements(By.XPATH, '//a[contains(@href, "/v-cars-trucks/")]')
    liens = set()
    for elem in elements:
        try:
            href = elem.get_attribute("href")
            if href and "/v-cars-trucks/" in href:
                clean_href = href.split("?")[0]
                liens.add(clean_href)
        except:
            continue
    return list(liens)

def collect_new_links():
    reset_scrape_state_if_needed()
    start_page = get_start_page()
    existing_links = read_existing_links()

    date_str = get_today_str()
    temp_file = f"warehouse/html/kijiji/nouveaux_liens_{date_str}.txt"
    os.makedirs(os.path.dirname(temp_file), exist_ok=True)
    open(temp_file, "w", encoding="utf-8").close()

    driver = webdriver.Chrome()
    page = start_page
    pages_sans_nouveaux = 0
    MAX_SANS_NOUVEAUX = 5
    total_nouveaux = 0

    while True:
        url = LISTING_URL.format(page)
        print(f"[Listing] Page {page} → {url}")
        try:
            driver.get(url)
        except Exception as e:
            print(f"Erreur page {page} : {e}")
            break

        liens_page = get_links_from_page(driver)
        print(f"→ {len(liens_page)} liens trouvés dans la page {page}")
        nouveaux = [l for l in liens_page if l not in existing_links]
        print(f"→ {len(nouveaux)} nouveaux liens dans la page {page}")

        if nouveaux:
            with open(temp_file, "a", encoding="utf-8") as tf:
                tf.write("\n".join(nouveaux) + "\n")
            with open(LIENS_PATH, "a", encoding="utf-8") as lf:
                lf.write("\n".join(nouveaux) + "\n")
            existing_links.update(nouveaux)
            total_nouveaux += len(nouveaux)
            pages_sans_nouveaux = 0
        else:
            pages_sans_nouveaux += 1

        with open(LAST_PAGE_PATH, "w") as f:
            f.write(str(page + 1))

        page += 1
        if pages_sans_nouveaux >= MAX_SANS_NOUVEAUX:
            print(f"Aucune nouvelle annonce trouvée depuis {MAX_SANS_NOUVEAUX} pages, arrêt.")
            break

    driver.quit()

    print(f"\n→ Total nouveaux liens trouvés : {total_nouveaux}")
    return temp_file, total_nouveaux

def save_html_files_from_links(temp_file):
    start_index = 0
    if os.path.exists(LAST_HTML_INDEX_PATH):
        try:
            with open(LAST_HTML_INDEX_PATH, "r") as f:
                start_index = int(f.read().strip())
        except:
            pass

    with open(temp_file, "r", encoding="utf-8") as f:
        liens = [line.strip() for line in f.readlines() if line.strip()]

    os.makedirs(WAREHOUSE_PATH, exist_ok=True)
    driver = webdriver.Chrome()

    for i, lien in enumerate(liens, start=start_index):
        try:
            driver.get(lien)
            time.sleep(random.uniform(0.6, 0.8))
            filename = os.path.join(WAREHOUSE_PATH, f"annonce_{i:05d}.html")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"[HTML] annonce_{i:05d}.html sauvegardé.")
            with open(LAST_HTML_INDEX_PATH, "w") as f:
                f.write(str(i + 1))
        except Exception as e:
            print(f"Erreur HTML {i:05d} → {e}")
            break

    driver.quit()

if __name__ == "__main__":
    temp_file, total = collect_new_links()
    if total > 0:
        save_html_files_from_links(temp_file)
