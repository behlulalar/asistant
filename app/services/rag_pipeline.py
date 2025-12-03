#RAG ZİNCİRİ SORU - CEVAP
import sys
import os

# Mevcut dosyanın konumunu al
current_dir = os.path.dirname(os.path.abspath(__file__))
# İki üst dizine (proje köküne) çık: app/services/ -> app/ -> ROOT
root_dir = os.path.abspath(os.path.join(current_dir, '../../'))
# Bu yolu Python'un arama listesine ekle
sys.path.append(root_dir)

from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from vector_store.chroma.chroma_db import db_baglantisi_kur

def zincir_getir():

    db = db_baglantisi_kur()

    kullanici = db.as_retriever(search_kwargs={"k": 5})

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    system_prompt = (
        "Sen Sakarya Uygulamalı Bilimler Üniversitesi (SUBÜ) Mevzuat Asistanısın. "
        "Görevin, öğrencilerin ve personelin yönetmeliklerle ilgili sorularını cevaplamak. "
        "Sadece sana aşağıda verilen 'Bağlam' (Context) içindeki bilgileri kullan. "
        "Eğer bağlamda cevabı bulamazsan 'Bu konuda yönetmeliklerde bilgi bulamadım' de, asla bilgi uydurma. "
        "Cevap verirken bilgiyi hangi dosyanın hangi maddesinden aldığını mutlaka belirt."
        "\n\n"
        "--- BAĞLAM (CONTEXT) ---\n"
        "{context}"
    )

    prompt_sablonu = ChatPromptTemplate.from_messages([
        ("system", system_prompt),

        MessagesPlaceholder(variable_name="chat_history"),

        ("human", "{input}"),
    ])

    soru_cevap = create_stuff_documents_chain(llm, prompt_sablonu)

    rag_zinciri = create_retrieval_chain(kullanici, soru_cevap)

    return rag_zinciri

if __name__ == "__main__":
    zincir = zincir_getir()
    cevap = zincir.invoke({"input": "Yaz okulunda en fazla kaç ders alabilirim? "})
    print("CEVAP:", cevap["answer"])