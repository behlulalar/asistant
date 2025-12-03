#DUZENLİ GUNCELLEME 

import schedule
import time 
import subprocess

def gorevi_calistir():
    print("PDF Kontrolü Başlıyor.")
    subprocess.run(["python", "pdf_downloader.py"])

schedule.every(12).hours.do(gorevi_calistir)
print("Otomatik PDF kontrol sistemi başlatıldı. Her 12 saatte bir çalışacak.")

while True:
    schedule.run_pending()
    time.sleep(60)