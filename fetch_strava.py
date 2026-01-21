import requests
import json
import os
import time

# GitHub Secrets'tan bilgileri al
CLIENT_ID = os.environ["STRAVA_CLIENT_ID"]
CLIENT_SECRET = os.environ["STRAVA_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["STRAVA_REFRESH_TOKEN"]

def get_access_token():
    """Refresh token kullanarak yeni bir Access Token alır."""
    print("Yeni Access Token alınıyor...")
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
        print(f"Hata! Token alınamadı: {response.text}")
        exit(1)
        
    return response.json()["access_token"]

def get_all_activities():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    all_activities = []
    page = 1
    per_page = 200 # Strava'nın izin verdiği maksimum sayfa boyutu
    
    print("Aktiviteler çekilmeye başlanıyor...")
    
    while True:
        print(f"Sayfa {page} taranıyor...")
        
        try:
            response = requests.get(
                f"https://www.strava.com/api/v3/athlete/activities?per_page={per_page}&page={page}",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"Hata! Sayfa {page} çekilemedi.")
                break
            
            data = response.json()
            
            # Eğer gelen veri boşsa, tüm aktiviteler bitmiş demektir
            if not data:
                print("Tüm aktiviteler çekildi.")
                break
            
            # Listeye ekle
            all_activities.extend(data)
            
            # Bir sonraki sayfaya geç
            page += 1
            
            # API'yi yormamak için çok kısa bekle
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Bir hata oluştu: {e}")
            break
            
    print(f"Toplam {len(all_activities)} adet ham veri bulundu. Filtreleniyor...")

    # SADECE HARİTASI OLANLARI VE GEREKLİ BİLGİLERİ AL (Dosya boyutu şişmesin)
    clean_data = []
    for act in all_activities:
        # Harita verisi (polyline) var mı kontrol et
        if act.get("map") and act["map"].get("summary_polyline"):
            clean_data.append({
                "name": act["name"],
                "distance": act["distance"],
                "start_date": act["start_date"],
                "map": act["map"]["summary_polyline"] # Şifreli harita verisi
            })
            
    print(f"Filtreleme bitti. {len(clean_data)} adet haritalı aktivite kaydedilecek.")

    # Veriyi dosyaya yaz
    with open("strava_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False)
    
    print("✅ BAŞARILI! Veriler 'strava_data.json' dosyasına kaydedildi.")

if __name__ == "__main__":
    get_all_activities()