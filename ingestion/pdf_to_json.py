import fitz
import os
import json 
import re 
from datetime import datetime 

def clean_text(metin: str) -> str:
    """
    PDF'ten çıkarılmış ham metni temizleyip sadeleştirir.
    Satır sonlarını, fazla boşlukları, sayfa numaralarını ve
    bozuk karakterleri düzeltir. Temiz metni döndürür.
    """

    # 1️⃣ Satır sonlarını tek satıra indir
    metin = metin.replace("\r", " ").replace("\n", " ")

    # 2️⃣ Fazla boşlukları sadeleştir
    metin = re.sub(r"\s+", " ", metin)

    # 3️⃣ Sayfa numarası, başlık, footer kalıntılarını sil
    metin = re.sub(r"(?i)sayfa\s*\d+(/\d+)?", "", metin)              # Sayfa 1/8 gibi ifadeler
    metin = re.sub(r"(?i)sakarya\s+uygulamal[ıi]\s+bilimler\s+üniversitesi", "", metin)
    metin = re.sub(r"(?i)yönerge\s+no[:\s]*\d*", "", metin)

    # 4️⃣ Türkçe karakter kodlama hatalarını düzelt
    replace_map = {
        "Ý": "İ", "Þ": "Ş", "ð": "ğ",
        "ý": "ı", "Ð": "Ğ", "þ": "ş",
        "Â": "A", "â": "a", "¢": "ç"
    }
    for eski, yeni in replace_map.items():
        metin = metin.replace(eski, yeni)

    # 5️⃣ Gereksiz özel karakterleri temizle
    metin = re.sub(r"[_~•■●◦▪▫❖►–—]", " ", metin)

    # 6️⃣ Fazla boşlukları yeniden sadeleştir
    metin = re.sub(r"\s+", " ", metin).strip()

    # 7️⃣ Çok kısa veya boş metinleri atla
    if len(metin) < 100:
        return None

    return metin



dosya_yolu = "data/pdfs"
json_klasoru = "data/json"

os.makedirs(json_klasoru, exist_ok=True)



for dosya in os.listdir(dosya_yolu):
    if dosya.lower().endswith(".pdf"):
        tam_yol = os.path.join(dosya_yolu, dosya)

        try:
            pdf = fitz.open(tam_yol)
            butun_metin = ""

            for sayfa in pdf:
                butun_metin += sayfa.get_text("text")

            temiz_metin = clean_text(butun_metin)

            if temiz_metin:
                json_veri = {
                    "file_name": dosya,
                    "page_count": pdf.page_count,
                    "hash": "placeholder_hash",
                    "source_url": "https://hukuk.subu.edu.tr/tr/yonergeler",
                    "extracted_at": datetime.now().isoformat(timespec='seconds'),
                    "content": temiz_metin
                }

                # JSON dosyasını oluştur
                json_yolu = os.path.join(json_klasoru, dosya.replace(".pdf", ".json"))

                with open(json_yolu, "w", encoding="utf-8") as f:
                    json.dump(json_veri, f, ensure_ascii=False, indent=4)

                print(f"✅ {dosya} temizlendi ve JSON olarak kaydedildi.")

            else:
                print(f"⚠️ {dosya} boş veya çok kısa, atlandı.")

        except Exception as e:
            print(f"❌ {dosya} okunamadı: {e}")

#Bu kısıma cok fazla hakim olmadıgım icin burayı chate yazdırdım. 