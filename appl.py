import streamlit as st
import os
import sys


# Python'un üst klasördeki modülleri bulabilmesi için yol ayarı
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_pipeline import zincir_getir # İsim karışıklığı olmasın diye senin import'u düzelttim
from vector_store.chroma.chroma_db import veri_isle_yukle
from langchain_core.messages import AIMessage, HumanMessage

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="SUBÜ Asistan", page_icon="🎓", layout="wide")

# --- CSS İLE GÜZELLEŞTİRME ---
st.markdown("""
<style>
    .stChatMessage { border-radius: 10px; }
    h1 { color: #2E86C1; }
    .stButton button { border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- SOL MENÜ (SIDEBAR) ---
with st.sidebar:
    # Logo varsa göster, yoksa hata vermesin diye try-except (veya path kontrolü)
    logo_path = "trbeyaz_yatay_logo.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.info("Logo bulunamadı, varsayılan görünüm kullanılıyor.")
        
    st.title("Ayarlar")
    st.divider()
    
    # 1. SOHBET GEÇMİŞİ YÖNETİMİ
    if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # 2. ADMIN PANELİ (VERİ GÜNCELLEME)
    st.subheader("🔧 Sistem Yönetimi")
    st.info("Bu alan veritabanını güncellemek içindir.")
    
    if st.button("🔄 Veritabanını Güncelle", type="primary", use_container_width=True):
        try:
            with st.status("Sistem güncelleniyor...", expanded=True) as status:
                st.write("📥 1. Yönergeler webden taranıyor (Simülasyon)...")
                # Buraya pdf_downloader fonksiyonunu ekleyebilirsin
                
                st.write("🧩 2. PDF'ler parçalanıyor ve işleniyor...")
                veri_isle_yukle()
                
                status.update(label="✅ Güncelleme Tamamlandı!", state="complete", expanded=False)
                st.success("Sistem güncellendi! Lütfen sayfayı yenileyin.")
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# --- ANA SOHBET ALANI ---
st.title("🎓 SUBÜ Mevzuat Asistanı")

# Session State Başlatma
if "messages" not in st.session_state:
    st.session_state.messages = []

# Eski Mesajları Ekrana Bas
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# --- ZİNCİRİ YÜKLE (CACHE) ---
@st.cache_resource
def sistemi_hazirla():
    return zincir_getir() # Fonksiyon ismini rag_pipeline.py dosyanla eşleştirdim

with st.spinner("Yapay zeka beyni yükleniyor..."):
    chain = sistemi_hazirla()

# --- SOHBET DÖNGÜSÜ ---
if prompt := st.chat_input("Sorunuzu yazın..."):
    
    # 1. Kullanıcı Mesajını Ekle ve Göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. HAFIZAYI HAZIRLA (GÜVENLİ VERSİYON)
    # LangChain'in anlayacağı formata çeviriyoruz
    chat_history = []
    for msg in st.session_state.messages[:-1]: # Son mesaj hariç eskiler
        icerik = msg.get("content")
        
        # HATA KORUMASI: İçerik boşsa (None) atla
        if icerik is None:
            continue
            
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=icerik))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=icerik))

    # 3. CEVAP ÜRETİMİ
    with st.chat_message("assistant"):
        with st.spinner("Yönetmelikler taranıyor..."):
            try:
                # Zinciri çalıştır (History + Input)
                response = chain.invoke({
                    "input": prompt,
                    "chat_history": chat_history
                })
                
                answer = response["answer"]
                
                # Cevabı Göster
                st.markdown(answer)
                
                # Kaynakları Göster (Expander)
                if "context" in response and response["context"]:
                    with st.expander("📚 Referans Kaynaklar (Tıkla)"):
                        unique_sources = set()
                        for doc in response["context"]:
                            source = doc.metadata.get("file_name", "Bilinmiyor")
                            if "/" in source:
                                source = source.split("/")[-1]
                            
                            page = doc.metadata.get("page_count", "-")
                            
                            if source not in unique_sources:
                                st.markdown(f"- 📄 **{source}** (Veri: {page})")
                                unique_sources.add(source)
                
                # Cevabı Kaydet
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Cevap üretilirken hata oluştu: {e}")