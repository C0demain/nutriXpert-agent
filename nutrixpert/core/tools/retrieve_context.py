import os
from langchain_community.vectorstores import Chroma
from nutrixpert.rag.rag_service import get_embeddings
from google.adk.tools import FunctionTool

CHROMA_PATH = "chroma_store"

def get_vectorstore():
    """Reabre banco vetorial já existente."""
    if os.path.exists(CHROMA_PATH):
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())
    return None

def retrieve_context(question: str, k: int = 3, score_threshold: float = 0.3) -> str:
    """Recupera chunks relevantes do banco vetorial + fallback glossário."""
    vectordb = get_vectorstore()
    if not vectordb:
        return ""

    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": k})
    results = retriever.get_relevant_documents(question)

    # Filtragem manual de resultados com base no score (quando disponível)
    filtered_results = []
    for r in results:
        score = r.metadata.get("score")
        if score is None or score >= score_threshold:
            filtered_results.append(r)

    # Monta string com metadados
    context = "\n\n".join([
        f"[Fonte: {r.metadata.get('source', 'desconhecida')}] {r.page_content}"
        for r in filtered_results
    ])

    # Fallback glossário manual
    termos_criticos = {
        "taco": "TACO = Tabela Brasileira de Composição de Alimentos (UNICAMP).",
        "imc": "IMC = Índice de Massa Corporal, peso(kg)/altura²(m).",
        "usda": "USDA FoodData Central = Base oficial de dados nutricionais dos EUA."
    }
    for termo, definicao in termos_criticos.items():
        if termo in question.lower():
            context += f"\n\n[Glossário] {definicao}"

    return context

retrieve_context_tool = FunctionTool(
    func=retrieve_context,
)
