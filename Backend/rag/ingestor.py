import json
import os
import sys

from langchain_ollama import OllamaEmbeddings
from rag.embeddings import add_batch_embeddings, delete_all_embeddings

FILE_PATH = "files/faqs.json"
embedder = OllamaEmbeddings(model="nomic-embed-text")

def ingest_faqs(path=FILE_PATH):
    if not os.path.exists(path):
        print("No encuentro faqs.json")
        return

    with open(path, "r", encoding="utf-8") as f:
        lista_faqs = json.load(f)

    print(f"Leyendo {len(lista_faqs)} FAQs manuales...")

    # delete_all_embeddings()

    items_to_insert = []
    
    textos_para_vectorizar = [item["pregunta"] for item in lista_faqs]
    
    print("Calculando embeddings de las preguntas...")
    vectores = embedder.embed_documents(textos_para_vectorizar)

    for i, item in enumerate(lista_faqs):
        faq_data = {
            # Lo que se mostrará al usuario (La respuesta)
            "text": f"Pregunta: {item['pregunta']}\nRespuesta: {item['respuesta']}",
            
            "group_name": "faq_empresa",
            "intent": "faq_manual",
            "embedding": vectores[i], 
            "meta": {"tipo": "faq_estatica"}
        }
        items_to_insert.append(faq_data)

    # 4. Guardar
    add_batch_embeddings(items_to_insert)
    print("FAQs manuales cargadas con éxito!")


if __name__ == "__main__":
    ingest_faqs(path=FILE_PATH)