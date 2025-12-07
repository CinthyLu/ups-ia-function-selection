import sys
import os

# Asegúrate de importar el Embedder
from langchain_ollama import OllamaEmbeddings 
from rag.embeddings import similarity_search

# 1. Configurar el mismo modelo que usaste para guardar (ingestor)
embedder = OllamaEmbeddings(model="nomic-embed-text")

preguntas_usuario = [
    # "¿A qué hora abren la tienda?",
    # "¿Dónde estan?",
    # "se me daño el producto, que hago?",
    # "¿Tienen envíos a Guayaquil?",
    # "¿Quiénes son ustedes?",
    # "¿Cuál es la mejor compu que tienen?",
    # "cuanto cuesta una coca cola",
    # "hola",
    # "¿Cómo puedo rastrear mi pedido?",
    # "¿Tienen descuentos para estudiantes?",
    "Predice el stock de la HP para mañana"
]


for pregunta in preguntas_usuario:
    print(f"    Pregunta Usuario: '{pregunta}'")
    
    query_vector = embedder.embed_query(pregunta) 
    
    resultados = similarity_search(
        query_embedding=query_vector, 
        top_k=3, 
        group_filter="faq_empresa", 
        threshold=0.5
    )
    
    if not resultados:
        print("El usuario preguntó algo que no está en nuestra base de conocimientos.")
    else:
        # Tomamos el mejor resultado
        mejor_match, distancia = resultados[0]
        print(f" Encontrado (Distancia: {distancia:.4f}):\n{mejor_match.text}")
    
    print("-" * 50)