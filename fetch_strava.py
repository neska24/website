import requests
import json
import os
import time

# GitHub Secrets'tan bilgileri al
CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

def get_access_token():
    print("🔑 Token yenileniyor...")
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
        print(f"❌ HATA: Token alınamadı! {response.text}")
        exit(1)
        
    return response.json()["access_token"]

def get_all_activities():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    all_activities = []
    page = 1
    per_page = 200 # Strava'nın izin verdiği maksimum sayı (Hızlı çekmesi için)
    
    print("🚀 Tüm aktiviteler çekilmeye başlanıyor...")
    
    while True:
        print(f"📄 Sayfa {page} taranıyor (Her sayfada {per_page} kayıt)...")
        
        try:
            response = requests.get(
                f"https://www.strava.com/api/v3/athlete/activities?per_page={per_page}&page={page}",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Hata! Sayfa {page} çekilemedi.")
                break
            
            data = response.json()
            
            # Liste boşsa veri bitmiş demektir
            if not data:
                print("🏁 Veriler bitti. Döngüden çıkılıyor.")
                break
            
            # Gelen veriyi listeye ekle
            all_activities.extend(data)
            
            print(f"   ✅ Bu sayfadan {len(data)} aktivite alındı.")
            
            page += 1
            # API'yi yormamak için kısa bekleme
            time.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Beklenmedik hata: {e}")
            break
            
    print(f"📊 TOPLAM {len(all_activities)} adet ham veri bulundu. Haritası olmayanlar eleniyor...")

    # SADECE HARİTASI (GPS DATASI) OLANLARI FİLTRELE
    clean_data = []
    for act in all_activities:
        if act.get("map") and act["map"].get("summary_polyline"):
            clean_data.append({
                "name": act["name"],
                "distance": act["distance"],
                "start_date": act["start_date"],
                "map": act["map"]["summary_polyline"]
            })
            
    print(f"💾 Filtreleme bitti. {len(clean_data)} adet haritalı aktivite 'strava_data.json' dosyasına kaydediliyor.")

    # Dosyayı kaydet
    with open("strava_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False)
    
    print("✅ İŞLEM BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    get_all_activities()
