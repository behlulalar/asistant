from app.services.rag_pipeline import zincir_getir
import textwrap

def sohbeti_baslat():

    print("Bot Hazırlanıyor...")

    zincir = zincir_getir()

    print("\n" + "="*50)
    print("🎓 SUBÜ Mevzuat Asistanı hazır! (Çıkış için 'q' yazın)")
    print("="*50 + "\n")

    while True:

        kullanici_girdisi = input("Soru: ")

        if kullanici_girdisi.lower() == "q":
            print("Tekrar görüşmek üzere!")
            break

        if not kullanici_girdisi:
            print("Lütfen bir soru yazınız!")
            continue


        print("Asistan Düşünüyor...")

        cevap = zincir.invoke({"input": kullanici_girdisi})

        print(f"\nCEVAP:\n{cevap['answer']}")

        print("\n" + "-"*30)
        print("📚 REFERANS KAYNAKLAR:")
        

        unique_sources = set() 
        
        if "context" in cevap:
            for belge in cevap["context"]:
                kaynak_adi = belge.metadata.get("file_name", "Bilinmeyen Kaynak")
            
                if "/" in kaynak_adi:
                    kaynak_adi = kaynak_adi.split("/")[-1]
                
                if kaynak_adi not in unique_sources:
                    print(f"📄 {kaynak_adi}")
                    unique_sources.add(kaynak_adi)
        else:
            print("Kaynak belirtilmedi.")
            
        print("-" * 30)

if __name__ == "__main__":
    sohbeti_baslat()