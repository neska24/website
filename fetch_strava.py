import requests
import json
import os
import time

CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

def get_access_token():
    print("🔑 Token alınıyor...")
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
    )
    if response.status_code != 200:
        print(f"❌ HATA: Token alınamadı! Strava cevabı: {response.text}")
        exit(1)
    return response.json()["access_token"]

def get_all_activities():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    all_activities = []
    page = 1
    
    print("📡 Strava'ya bağlanılıyor...")
    
    while True:
        print(f"--- Sayfa {page} taranıyor ---")
        response = requests.get(
            f"https://www.strava.com/api/v3/athlete/activities?per_page=20&page={page}", # Azar azar çekip kontrol edelim
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ HATA: Veri çekilemedi. Kod: {response.status_code}")
            break
            
        data = response.json()
        if not data:
            print("🏁 Strava'dan gelen liste boş. Başka aktivite yok.")
            break
            
        # DETAYLI RAPOR (Burada sorunu göreceğiz)
        print(f"✅ Bu sayfada {len(data)} aktivite bulundu. İnceleme başlıyor:")
        
        for act in data:
            has_map = False
            if act.get("map") and act["map"].get("summary_polyline"):
                has_map = True
                
            print(f"   🏃 Aktivite: {act['name']} (Gizlilik: {act.get('visibility', 'Bilinmiyor')}) -> Harita Var mı?: {'EVET' if has_map else 'HAYIR ❌'}")
            
            if has_map:
                all_activities.append(act)
        
        page += 1
        if page > 3: # Test için sadece ilk 3 sayfaya bakalım (60 aktivite)
            print("🛑 Test amaçlı 3. sayfada duruyoruz.")
            break
        time.sleep(1)

    print(f"📊 SONUÇ: Toplam {len(all_activities)} adet haritalı aktivite filtrelendi.")

    clean_data = []
    for act in all_activities:
        if act.get("map") and act["map"].get("summary_polyline"):
            clean_data.append({
                "name": act["name"],
                "distance": act["distance"],
                "start_date": act["start_date"],
                "map": act["map"]["summary_polyline"]
            })

    with open("strava_data.json", "w") as f:
        json.dump(clean_data, f)
    print("💾 Dosya kaydedildi.")

if __name__ == "__main__":
    get_all_activities()
