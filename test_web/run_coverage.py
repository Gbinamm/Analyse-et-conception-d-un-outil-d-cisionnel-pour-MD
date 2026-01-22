import subprocess
import time
import os
import sys
import signal
from Selenium_test_web import run_selenium_test 

def run_app_with_coverage():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    app_dir = os.path.join(root_dir, "application")
    app_path = os.path.join(app_dir, "app.py")
    
    log_dir = os.path.join(current_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    TEST_PORT = "8501"

    print(f"🧹 Nettoyage des anciens processus...")
    if os.name == 'nt':
        subprocess.run("taskkill /f /im streamlit.exe /t", shell=True, capture_output=True)

    print(f"🚀 Lancement de Coverage sur le port {TEST_PORT}...")

    env = os.environ.copy()
    env["PYTHONPATH"] = app_dir + os.pathsep + env.get("PYTHONPATH", "")
    env["TEST_MODE"] = "1"

    # Commande modifiée : suppression de shell=True pour une meilleure gestion des signaux
    cmd = [
        sys.executable, "-m", "coverage", "run", 
        f"--source={app_dir}", 
        "-m", "streamlit", "run", app_path, 
        f"--server.port={TEST_PORT}", 
        "--server.headless=true"
    ]
    
    # Lancement sans shell=True pour que proc.pid soit directement celui de coverage
    proc = subprocess.Popen(cmd, env=env, stdout=sys.stdout, stderr=sys.stderr, cwd=app_dir)
    
    print(f"⏳ Attente de l'initialisation de Streamlit (20s)...")
    time.sleep(20) 
    
    try:
        run_selenium_test()
    except Exception as e:
        print(f"❌ Erreur critique durant l'exécution : {e}")
    finally:
        print("🛑 Fermeture du serveur et sauvegarde du coverage...")
        if os.name == 'nt':
            # 1. On tente d'abord sans le /F (fermeture propre)
            subprocess.run(["TASKKILL", "/PID", str(proc.pid), "/T"], capture_output=True)
            time.sleep(2) 
            # 2. Si le processus résiste encore, on peut forcer, mais souvent coverage a déjà écrit
            subprocess.run(["TASKKILL", "/F", "/PID", str(proc.pid), "/T"], capture_output=True)
        else:
            os.kill(proc.pid, signal.SIGINT)
        
        time.sleep(5) # Temps crucial pour que le fichier .coverage soit écrit sur le disque
        print(f"\n📊 GÉNÉRATION DES RAPPORTS DANS : {log_dir}")
        subprocess.run([sys.executable, "-m", "coverage", "report"])
        subprocess.run([sys.executable, "-m", "coverage", "html", "-d", log_dir])
        print(f"📂 Rapport HTML disponible : {os.path.join(log_dir, 'index.html')}")

if __name__ == "__main__":
    run_app_with_coverage()