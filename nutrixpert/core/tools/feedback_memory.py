import uuid
from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import Optional

# Inicializa cliente local do Chroma (sem servidor externo)
client = Client(Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection("feedback_memory")
model = SentenceTransformer("all-MiniLM-L6-v2")

def add_feedback_to_memory(feedback_id: int, comentario: str, nota: int, user_id: str):
    """
    Adiciona um feedback ao índice vetorial para aprendizado futuro.
    """
    if not comentario:
        return
    
    embedding = model.encode(comentario)
    
    # gera um ID único baseado no feedback_id (ou UUID)
    chroma_id = f"fb_{feedback_id}_{uuid.uuid4().hex}"
    
    collection.add(
        ids=[chroma_id],
        documents=[comentario],
        embeddings=[embedding],
        metadatas={
            "feedback_id": feedback_id,
            "user_id": user_id,
            "nota": nota,
        }
    )

def search_related_feedbacks(query: str, user_id: Optional[str] = None, top_k: int = 3):
    """
    Busca feedbacks relacionados no índice vetorial.
    Se user_id for fornecido, filtra feedbacks daquele usuário.
    """
    
    embedding = model.encode(query)
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=filters or None
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return [
        {"comentario": d, "nota": m.get("nota"), "user_id": m.get("user_id")}
        for d, m in zip(docs, metas)
    ]