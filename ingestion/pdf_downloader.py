from fetch import fetch_file
import requests
import hashlib
import json 
import os 

# 🔸 HASH HESAPLAMA FONKSİYONU
def dosya_hash_hesapla(dosya_yolu):
    """Verilen dosyanın SHA-256 hash değerini hesaplar."""
    hash_obj = hashlib.sha256()
    with open(dosya_yolu, "rb") as f:
        for parca in iter(lambda: f.read(4096), b""):
            hash_obj.update(parca)
    return hash_obj.hexdigest()


# 🔸 HASH KAYDETME / GÜNCELLEME FONKSİYONU
def hash_kaydet(belge_adi, hash_degeri, hash_dosyasi="data/hashes.json"):
    """Hashes.json dosyasına yeni hash ekler veya günceller."""
    # hashes.json yoksa oluştur
    if not os.path.exists(hash_dosyasi):
        with open(hash_dosyasi, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    # mevcut hashleri yükle
    with open(hash_dosyasi, "r", encoding="utf-8") as f:
        try:
            hashes = json.load(f)
        except json.JSONDecodeError:
            hashes = {}

    # güncelle
    hashes[belge_adi] = hash_degeri

    # kaydet
    with open(hash_dosyasi, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=4)

def mevcut_hashleri_yukle(hash_dosyasi="data/hashes.json"):
    """Mevcut hash verilerini yükler."""
    if not os.path.exists(hash_dosyasi):
        return {}
    try:
        with open(hash_dosyasi, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}



qdms = fetch_file("https://hukuk.subu.edu.tr/tr/yonergeler")
print(len(qdms))

mevcut_hashler = mevcut_hashleri_yukle()


for links in qdms:
    link_kontrol = requests.get(links["url"], stream=True, timeout=10)
    id_degeri = links["url"].split("L=")[-1].split("&")[0]

    if link_kontrol.status_code != 200:
        print("Bağlantıda bir sıkıntı görünüyor.")
    else : 
        
        belge_adi = links["name"]
        belge_adi = belge_adi.lower()
        harfler = { "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
        "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"}

        for harf in harfler:
            belge_adi = belge_adi.replace(harf, harfler[harf])
        
        belge_adi = belge_adi.replace(" ","_")

        yasak_sembol = ':;,.!?()[]{}"\'\\|/'
        for i in yasak_sembol:
            belge_adi = belge_adi.replace(i, "")

        belge_adi = belge_adi.strip()

        if not belge_adi.endswith(".pdf"):
            belge_adi += ".pdf"
    
        dosya_yolu = "data/pdfs/" + belge_adi

    with open(dosya_yolu, "wb") as f:
        for parca in link_kontrol.iter_content(chunk_size=1024):
            if parca:
                f.write(parca)

    hash_degeri = dosya_hash_hesapla(dosya_yolu)
    hash_kaydet(belge_adi, hash_degeri)       
    mevcut_hashler[belge_adi] = hash_degeri

    print((f"{belge_adi}_{id_degeri} basariyla indirildi."))

