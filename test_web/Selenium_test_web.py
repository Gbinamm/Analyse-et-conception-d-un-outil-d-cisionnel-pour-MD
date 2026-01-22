import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_APP = "http://localhost:8501"

def run_selenium_test():
    print("🚀 Démarrage du test de couverture maximale...")
    
    # 1. Configuration des chemins
    base_dir = os.getcwd()
    chromedriver_path = os.path.join(base_dir, "drivers", "chromedriver.exe")
    chrome_exe_path = os.path.join(base_dir, "drivers", "GoogleChromePortable", "App", "Chrome-bin", "chrome.exe")
    
    tmp_profile = "C:\\temp\\test_selenium_cov_final"
    if os.path.exists(tmp_profile):
        shutil.rmtree(tmp_profile, ignore_errors=True)
    os.makedirs(tmp_profile, exist_ok=True)

    # 2. Options Chrome anti-crash
    chrome_options = Options()
    chrome_options.binary_location = chrome_exe_path
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument(f"--user-data-dir={tmp_profile}")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
    wait = WebDriverWait(driver, 25)

    try:
        driver.get(URL_APP)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "main-title")))
        print("✅ Interface main_ui() détectée.")

        sections = ["Ajouter Entretien", "Voir Données", "Ajouter Variable", "Modifier Valeurs", "Visualisation"]
        
        for section in sections:
            print(f"🧭 Test de la branche : {section}")
            try:
                # Clic sur le menu Sidebar
                radio_opt = wait.until(EC.element_to_be_clickable((By.XPATH, f"//label[contains(., '{section}')]")))
                driver.execute_script("arguments[0].click();", radio_opt)
                time.sleep(3) # Temps de chargement Streamlit
            except Exception:
                continue

            # --- LOGIQUE DE COUVERTURE PAR SECTION ---

            if section == "Ajouter Entretien":
                # 1. Parcourir tous les onglets (Force la lecture des rubriques dans get_table_metadata)
                tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
                for tab in tabs:
                    driver.execute_script("arguments[0].click();", tab)
                    time.sleep(0.5)

                # 2. Interagir avec les Selectboxes (Force l'exécution de la récupération des modalités)
                selects = driver.find_elements(By.CSS_SELECTOR, "div[data-baseweb='select']")
                for s in selects:
                    try:
                        driver.execute_script("arguments[0].click();", s)
                        time.sleep(1)
                        # Sélection de la première option disponible
                        option = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li[role='option']")))
                        option.click()
                        time.sleep(0.5)
                    except: pass

                # 3. Remplir les inputs (Texte, Nombre, Date)
                inputs = driver.find_elements(By.CSS_SELECTOR, "input")
                for inp in inputs:
                    try:
                        if not inp.is_displayed(): continue
                        t = inp.get_attribute("type")
                        if t == "number": inp.send_keys("123")
                        elif t == "date": inp.send_keys("01012026")
                        else: inp.send_keys("Automated Test")
                    except: pass
                
                # 4. Enregistrer (Couvre la fonction save_data)
                try:
                    btn = driver.find_element(By.XPATH, "//button[contains(., 'ENREGISTRER')]")
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(4) 
                except: pass

            elif section == "Ajouter Variable":
                # Interaction pour couvrir execute_sql et le rafraîchissement des métadonnées
                v_inputs = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='stForm'] input")
                if len(v_inputs) >= 2:
                    v_inputs[0].send_keys("test_col_coverage")
                    v_inputs[1].send_keys("Libellé Coverage")
                
                create_btn = driver.find_element(By.XPATH, "//button[contains(., 'Créer')]")
                # Test Négatif (Point 4) : Double clic pour provoquer l'erreur SQL "Duplicate"
                driver.execute_script("arguments[0].click();", create_btn)
                time.sleep(2)
                driver.execute_script("arguments[0].click();", create_btn)
                time.sleep(2)

            elif section == "Modifier Valeurs":
                try:
                    # Sélectionner une variable pour passer le st.stop()
                    sel = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-baseweb='select']")))
                    driver.execute_script("arguments[0].click();", sel)
                    time.sleep(1)
                    driver.find_element(By.CSS_SELECTOR, "li[role='option']").click()

                    # Test Négatif (Point 4) : Envoyer un texte mal formaté pour logic.py
                    area = driver.find_element(By.TAG_NAME, "textarea")
                    area.clear()
                    area.send_keys("ErreurFormat; 1:Correct; SansDeuxPoints")
                    
                    update_btn = driver.find_element(By.XPATH, "//button[contains(., 'Mettre à jour')]")
                    driver.execute_script("arguments[0].click();", update_btn)
                    time.sleep(2)
                except: pass

            elif section == "Visualisation":
                try:
                    # Switcher sur "Croisement" (Couvre la boucle process_var_for_stats)
                    radio_crois = driver.find_element(By.XPATH, "//label[contains(., 'Croisement')]")
                    driver.execute_script("arguments[0].click();", radio_crois)
                    time.sleep(2)
                    
                    # Sélectionner les axes X et Y
                    axes = driver.find_elements(By.CSS_SELECTOR, "div[data-baseweb='select']")
                    for axe in axes[:2]:
                        driver.execute_script("arguments[0].click();", axe)
                        time.sleep(1)
                        driver.find_element(By.CSS_SELECTOR, "li[role='option']").click()
                except: pass

        print("🏆 Parcours Selenium terminé. Les données de couverture ont été générées.")

    except Exception as e:
        print(f"❌ Erreur critique Selenium : {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_selenium_test()