from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from dotenv import load_dotenv
import json, os, shutil 


DB_YOLU = "vector_store/chroma"
JSON_DIR = "data/json"
KOLEKSİYON_ADI = "subu_yonergeler"

load_dotenv()


def db_baglantisi_kur():

    EMBEDDING_MODEL_NAME = OpenAIEmbeddings(model = "text-embedding-3-large")

    db = Chroma(
        persist_directory=DB_YOLU,
        embedding_function=EMBEDDING_MODEL_NAME,
        collection_name=KOLEKSİYON_ADI
    )
    return db 

def eski_db_temizle():
    if os.path.exists(DB_YOLU):
        shutil.rmtree(DB_YOLU)
        print("Eski veritabanı temizlendi!")

def veri_isle_yukle():
    print(f"{JSON_DIR} içerisindeki dosyalar işleniyor.")

    belgeler_listesi = []

    if not os.path.exists(JSON_DIR): 
        print(f"HATA: {JSON_DIR} klasörü bulunamadı!")
        return

    for dosya_adi in os.listdir(JSON_DIR):
        if dosya_adi.endswith(".json"):
            dosya_yolu = os.path.join(JSON_DIR, dosya_adi)

            with open(dosya_yolu, "r", encoding="utf-8") as f: 
                veri = json.load(f)

                main_content = veri.get("content", "")

                metadata = {
                    "file_name": dosya_adi,
                    "hash": veri.get("hash", "hash_yok"),
                    "source_url": veri.get("source_url", ""),
                    "page_count": veri.get("page_count", "")
                }

                yeni_belge = Document(page_content=main_content, metadata=metadata)
                belgeler_listesi.append(yeni_belge)

    print(f"Toplam {len(belgeler_listesi)} adet tarif dosyası hafızaya alındı.")

    parcalama = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=400,
        separators= ["MADDE", "Article", "\n\n", "\n"] #bu kısımı deneyerek en iyi hale getirmenin yollarını bul!
    )

    parcalanmis_belgeler = parcalama.split_documents(belgeler_listesi)
    print(f"Yönergeler {len(parcalanmis_belgeler)} küçük parçaya bölündü.")

    if parcalanmis_belgeler:
        db = db_baglantisi_kur()

        batch_size = 100 
        toplam_parca = len(parcalanmis_belgeler)

        print("Veritabanına yükleme başlıyor.")
        for i in range(0, toplam_parca, batch_size):
            paket = parcalanmis_belgeler[i : i + batch_size]
            db.add_documents(paket)
            print(f"   ... {i + len(paket)} / {toplam_parca} tamamlandı.")

        print("Tüm yönergeler başarıyla yüklendi!")
    else : 
        print("Yüklenecek veri bulunamadı!")
    
if __name__ == "__main__": 
    veri_isle_yukle()
