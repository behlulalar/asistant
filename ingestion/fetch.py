from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def fetch_file(url:str):
    url = "https://hukuk.subu.edu.tr/tr/yonergeler"

    headers = { "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"}

    qdms_links = []

    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, "html.parser")

    liste = soup.find("div", {"class" : "content-main"}).find_all("li")
    if not liste : 
        print("Sayfa yapısı değişmiş olabilir. Lütfen yetkiliye danışın.")
        return[]

    for item in liste:
        yonerge_adi = item.find("a", href = True)

        if yonerge_adi and "qdms" in yonerge_adi["href"].lower():
            full_url = urljoin(url, yonerge_adi["href"])
            name = yonerge_adi.text.strip() or full_url.split("/")[-1]
            qdms_links.append({
                "name": name,
                "url": full_url
            })
    return qdms_links


if __name__ == "__main__":
    qdms_links = fetch_file("https://hukuk.subu.edu.tr/tr/yonergeler")
    for item in qdms_links:
        print(f"- {item['name']} → {item['url']}")
    