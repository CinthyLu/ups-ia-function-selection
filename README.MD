
# UPS AI Assistant - Function Matching & Predictions

[![FastAPI](https://img.shields.io/badge/FastAPI-Modern%20API-red)](https://fastapi.tiangolo.com/) [![React](https://img.shields.io/badge/React-Frontend-blue)](https://reactjs.org/) [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Vector%20DB-brightgreen)](https://postgresql.org/) [![Docker](https://img.shields.io/badge/Docker-Container-blue)](https://docker.com/)

**Aplicación de IA para consultas universitarias (UPS) con Function Matching inteligente, predicciones de inventario y RAG para FAQs.**

## ✨ ¿Qué hace la app?

### Funcionalidades principales:

1. **Function Matcher (IA)**: Convierte consultas del usuario en llamadas automáticas a funciones usando embeddings + KNN (similitud coseno >90%)
2. **Predicciones de inventario**: ML para stock con opciones por producto, fecha o general
3. **Chatbot universitario**: Respuestas sobre admisiones, becas, mallas curriculares
4. **RAG + FAQs**: Retrieval Augmentation con documentos de la universidad
5. **Frontend React**: Interfaz moderna para chat y predicciones

**Ejemplos de consultas que entiende:**
```

"Con quién me contacto para admisiones en la UPS"
"Cuáles son los tipos de becas"
"Malla curricular de computación"


```

---

## 🚀 Quick Start

### 1. Backend (FastAPI + Postgres)

```bash
# 1. Levantar base de datos
docker compose up -d

# 2. Inicializar Function Matcher (IMPORTANTE)
cd Backend/ai/functionMatcher/
python Initializer.py

# 3. Crear tablas FAQs
cd Backend/db/
python models.py
python Tables.py  # rellena datos

# 4. Configurar API Key (Gemini)
echo 'GOOGLE_GEMINI_API_KEY=tu_api_key_aqui' > .env

# 5. Correr aplicación
python main.py
```

**Backend disponible en:** `http://localhost:8000`

### 2. Frontend (React)

```bash
cd Frontend/
npm install
npm run dev
```

**Frontend disponible en:** `http://localhost:3000`

---

## 🔧 API Endpoints

| Endpoint | Descripción | Ejemplo |
| :-- | :-- | :-- |
| `POST /chat` | Chat con function matching | `{"query": "malla de computación"}` |
| `POST /predict/stock` | Predicción stock general | `{}` |
| `POST /predict/stock/product/{id}` | Stock por producto | `{}` |
| `POST /predict/stock/date/{date}` | Stock por fecha | `{}` |
| `POST /predict/stock/product-date` | Stock producto + fecha | `{"product_id": 1}` |

**Docs automáticos:** `http://localhost:8000/docs`

---

## 🏗️ Arquitectura

```
Usuario → React Frontend → FastAPI Backend
                    ↓
            Function Matcher (KNN + Embeddings)
                    ↓
        Predicciones ML / RAG / FAQs / Gemini
                    ↓
             PostgreSQL (vectores + datos)
```

**Tecnologías:**

- **Backend**: FastAPI, PostgreSQL (vectores), Gemini LLM
- **IA**: Sentence Transformers, scikit-learn (KNN), embeddings
- **Frontend**: React, TypeScript
- **Infra**: Docker Compose

---

## 📊 Function Matching (cómo funciona)

1. **Query** → Embedding
2. **Comparación** con descripciones de funciones (similitud coseno)
3. **Selección** función más cercana (>90% confianza)
4. **Ejecución** y respuesta natural

**Ejemplo:**

```
Query: "becas UPS"
→ Selecciona: fn_tipos_becas()
→ Respuesta: "Becas 30%, 40%, 50%"
```


---

## 🔄 Comandos útiles

```bash
# Reentrenar matcher
python Backend/ai/functionMatcher/retrain.py

# Reiniciar todo
docker compose down -v && docker compose up -d
cd Backend/ai/functionMatcher/ && python Initializer.py
```


---

<!-- ## 🚧 TODO (Pendiente)

- ✅ Function Matching (embeddings + KNN)
- ✅ Predicciones stock (todas las variantes)
- ✅ RAG para FAQs
- ✅ Carga CSV productos
- ⏳ **Extraer parámetros SQL en matcher** (routes.py ln 140)
- ⏳ **Reentrenamiento dinámico**
- ⏳ **Productos más/menos vendidos**
- ⏳ **Reportes CSV/Excel** -->

---

## 🛠️ Desarrollo

### Dependencias Backend

```bash
pip install -r Backend/requirements.txt
```


### Dependencias Frontend

```bash
cd Frontend/ && npm install
```


### Agregar nueva función

1. `Backend/ai/functionMatcher/functions.py` → nueva función
2. `matching.py` → agregar al `FUNCTION_CATALOG`
3. `python Initializer.py` → reentrenar

---

## 📱 Testing

**Probar chat:**

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "malla curricular de arquitectura"}'
```

**Ver similitudes (debug):**
El endpoint `/chat` devuelve `function` y `similarity`.

---


