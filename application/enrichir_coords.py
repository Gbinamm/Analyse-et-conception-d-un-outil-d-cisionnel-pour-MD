import pandas as pd
import requests
import urllib.parse
import time
from sqlalchemy import create_engine, text

# Config tirée de ton app.py
DB_CONFIG = {
    "dbname": "postgres", "user": "postgres.hadygnmrwynnrlsekrwd",
    "password": "GabinBase2026", "host": "aws-1-eu-west-1.pooler.supabase.com", "port": "6543"
}

safe_user = urllib.parse.quote_plus(DB_CONFIG['user'])
safe_password = urllib.parse.quote_plus(DB_CONFIG['password'])
conn_url = f"postgresql://{safe_user}:{safe_password}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}?sslmode=require"
engine = create_engine(conn_url)

def get_coords(city_name):
    try:
        # Nettoyage minimal : on garde le nom brut pour l'API
        q = city_name.split(' ')[0].strip()
        url = "https://api-adresse.data.gouv.fr/search/"
        # Requests gère TOUT l'encodage (accents, espaces) proprement via params
        resp = requests.get(url, params={"q": q, "postcode": "56", "limit": 1}, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("features"):
                lon, lat = data["features"][0]["geometry"]["coordinates"]
                return lat, lon
        return None, None
    except: return None, None

def run_enrichment():
    print("--- DEMARRAGE ---")
    df = pd.read_sql("SELECT code_c, nom_c FROM public.commune WHERE lat IS NULL", engine)
    print(f"Communes a traiter : {len(df)}")
    
    with engine.connect() as conn:
        for i, row in df.iterrows():
            lat, lon = get_coords(row['nom_c'])
            if lat:
                conn.execute(text("UPDATE public.commune SET lat=:la, lon=:lo WHERE code_c=:id"),
                             {"la": lat, "lo": lon, "id": row['code_c']})
                print(f"[{i+1}] OK : {row['nom_c']}")
            time.sleep(0.2)
        conn.commit()
    print("--- TERMINE ---")

if __name__ == "__main__":
    run_enrichment()