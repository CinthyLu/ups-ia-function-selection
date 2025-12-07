"""
vectorstore.py
Manejo de embeddings para RAG en PostgreSQL usando pgvector + SQLAlchemy.

Responsabilidades:
- Tabla rag_embeddings (texto, grupo, intención, meta, embedding)
- Crear tablas
- Insertar 1 o muchos embeddings
- Buscar por similitud
"""

from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import Column, Integer, Text, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, func
from db.models import Base, engine, SessionLocal



# ==========================
# MODELO ORM PARA RAG
# ==========================

class RAGEmbedding(Base):
    """
    Tabla para embeddings del sistema RAG (intenciones, FAQs, descripciones, etc.)

    Campos clave:
      - text: texto base asociado al embedding
      - group_name: grupo general (ej. "prediccion", "faq", "saludo")
      - intent: intención específica (ej. "prediccion_por_producto_y_fecha")
      - meta: JSON con info extra (ej. parámetros esperados, ejemplo de prompt, etc.)
      - embedding: vector(768) almacenado con pgvector
    """
    __tablename__ = "rag_embeddings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    group_name = Column(String(100), nullable=False, index=True)
    intent = Column(String(150), nullable=False, index=True)
    meta = Column(JSONB, nullable=True)
    embedding = Column(Vector(768), nullable=False)

    def __repr__(self) -> str:
        return f"<RAGEmbedding(id={self.id}, group='{self.group_name}', intent='{self.intent}')>"


# ==========================
# UTILIDADES DE INICIALIZACIÓN
# ==========================

from sqlalchemy import text

def create_vector_tables() -> None:
    """
    Crea la extensión vector (si no existe) y luego las tablas necesarias.
    """
    with engine.connect() as conn:
        # Crear extensión vector si no existe
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # Crear tablas
    Base.metadata.create_all(engine)
    print("✓ Extensión vector verificada y tablas creadas")


# ==========================
# HELPERS DE SESIÓN
# ==========================

def get_db_session() -> Session:
    """Devuelve una sesión nueva."""
    return SessionLocal()


# ==========================
# INSERCIÓN DE EMBEDDINGS
# ==========================

def add_embedding(
    text: str,
    group_name: str,
    intent: str,
    embedding: List[float],
    meta: Optional[Dict[str, Any]] = None,
    session: Optional[Session] = None
) -> int:
    """
    Inserta UN embedding en la tabla rag_embeddings.

    Returns:
        id del registro creado.
    """
    own_session = False
    if session is None:
        session = get_db_session()
        own_session = True

    try:
        rag = RAGEmbedding(
            text=text,
            group_name=group_name,
            intent=intent,
            meta=meta or {},
            embedding=embedding
        )
        session.add(rag)
        session.commit()
        session.refresh(rag)
        return rag.id
    except Exception as e:
        session.rollback()
        print(f"✗ Error insertando embedding: {e}")
        raise
    finally:
        if own_session:
            session.close()


def add_batch_embeddings(
    items: List[Dict[str, Any]],
    session: Optional[Session] = None
) -> int:
    """
    Inserta varios embeddings en una sola transacción.

    Cada ítem del listado debe tener:
        {
          "text": str,
          "group_name": str,
          "intent": str,
          "embedding": List[float],
          "meta": Optional[dict]
        }

    Returns:
        Número de registros insertados.
    """
    if not items:
        return 0

    own_session = False
    if session is None:
        session = get_db_session()
        own_session = True

    try:
        objs = []
        for it in items:
            obj = RAGEmbedding(
                text=it["text"],
                group_name=it["group_name"],
                intent=it["intent"],
                embedding=it["embedding"],
                meta=it.get("meta", {})
            )
            objs.append(obj)

        session.add_all(objs)
        session.commit()
        return len(objs)
    except Exception as e:
        session.rollback()
        print(f"✗ Error en add_batch_embeddings: {e}")
        raise
    finally:
        if own_session:
            session.close()


# ==========================
# BÚSQUEDA SEMÁNTICA
# ==========================


def similarity_search(
    query_embedding: List[float],
    top_k: int = 3,                
    group_filter: Optional[str] = None,
    intent_filter: Optional[str] = None,
    threshold: float = 0.4,      
    session: Optional[Session] = None
) -> List[Tuple[RAGEmbedding, float]]:
    """
    Busca los embeddings más cercanos usando distancia coseno.
    Incluye un filtro de umbral para descartar coincidencias irrelevantes.
    """
    own_session = False
    if session is None:
        session = get_db_session()
        own_session = True

    try:
        # 1. Definir la expresión de distancia (Coseno)
        # Nota: En pgvector con cosine_distance: 0 es igual, 1 es opuesto.
        # Queremos distancias BAJAS.
        distance_expr = RAGEmbedding.embedding.cosine_distance(query_embedding)

        # 2. Construir la Query base
        query = session.query(RAGEmbedding, distance_expr.label("distance"))

        # 3. Filtros Opcionales (Metadata)
        if group_filter:
            query = query.filter(RAGEmbedding.group_name == group_filter)
        
        if intent_filter:
            query = query.filter(RAGEmbedding.intent == intent_filter)

        # 4. FILTRO DE UMBRAL (La clave del éxito)
        # Solo devolver registros si la distancia es MENOR al umbral.
        # Esto evita que devuelva basura si la pregunta no tiene nada que ver.
        query = query.filter(distance_expr < threshold)

        # 5. Ordenar y Limitar
        results = (
            query.order_by(distance_expr)  # Ordenar de menor distancia (más parecido) a mayor
            .limit(top_k)
            .all()
        )

        # Retorna: Lista de tuplas [(ObjetoRAG, 0.12), (ObjetoRAG, 0.15)]
        return results

    except Exception as e:
        print(f"✗ Error en similarity_search: {e}")
        return [] # Retornar lista vacía en error para no romper el flujo
    finally:
        if own_session:
            session.close()

def delete_all_embeddings() -> int:
    """
    Borra TODOS los embeddings del vectorstore.
    Úsalo con cuidado.
    """
    session = get_db_session()
    try:
        deleted = session.query(RAGEmbedding).delete()
        session.commit()
        print(f"Embeddings eliminados: {deleted}")
        return deleted
    except Exception as e:
        session.rollback()
        print(f"✗ Error borrando embeddings: {e}")
        raise
    finally:
        session.close()


# ==========================
# EJEMPLO DE USO DIRECTO
# ==========================

if __name__ == "__main__":
    print("=== Inicializando vectorstore RAG ===")
    create_vector_tables()

    # Ejemplo: insertar 2 intenciones
    dummy_emb = [0.1] * 1536  # solo para prueba, usa embeddings reales

    add_embedding(
        text="Quiero ver la predicción de stock por producto y fecha",
        group_name="prediccion",
        intent="prediccion_por_producto_y_fecha",
        embedding=dummy_emb,
        meta={"tipo": "intent", "descripcion": "Predice stock para un producto en una fecha específica"}
    )

    add_embedding(
        text="Hola, buenos días",
        group_name="saludo",
        intent="saludo_general",
        embedding=dummy_emb,
        meta={"tipo": "intent", "descripcion": "Saludo estándar"}
    )

