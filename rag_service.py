import os
import pandas as pd
import pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

CHROMA_PATH = "chroma_store"

# --------- Loaders ---------
def load_pdf(path: str) -> str:
    """Extrai texto de um PDF."""
    with pdfplumber.open(path) as pdf:
        return "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

def load_xlsx(path: str) -> str:
    """Extrai dados tabulares de um XLSX (TACO)."""
    df = pd.read_excel(path, sheet_name="Taco")

    lines = []
    for _, row in df.iterrows():
        alimento = row.get("Descrição do Alimento", "")
        comps = [
            f"{col}: {row[col]}"
            for col in df.columns
            if col != "Descrição do Alimento" and pd.notna(row[col])
        ]
        lines.append(f"{alimento} -> {', '.join(comps)}")

    return "\n".join(lines)


def ingest_documents(folder="documents"):
    """Carrega todos os PDFs e XLSX da pasta documents."""
    docs = []
    if not os.path.exists(folder):
        return docs
    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if fname.lower().endswith(".pdf"):
            text = load_pdf(path)
            docs.append({"text": text, "metadata": {"source": fname, "type": "pdf"}})
        elif fname.lower().endswith(".xlsx"):
            text = load_xlsx(path)
            docs.append({"text": text, "metadata": {"source": fname, "type": "taco"}})
    return docs

# --------- Embeddings Locais ---------
def get_embeddings():
    """Usa modelo local do HuggingFace para gerar embeddings."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --------- Vetorização ---------
def build_vectorstore(docs):
    """Divide em chunks, gera embeddings e salva no Chroma."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = []
    for doc in docs:
        for chunk in splitter.split_text(doc["text"]):
            chunks.append(Document(page_content=chunk, metadata=doc["metadata"]))

    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    vectordb.persist()
    return vectordb

def get_vectorstore():
    """Reabre banco vetorial já existente."""
    if os.path.exists(CHROMA_PATH):
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embeddings())
    return None

def retrieve_context(question: str, k: int = 3) -> str:
    """Recupera chunks relevantes do banco vetorial."""
    vectordb = get_vectorstore()
    if not vectordb:
        return ""
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    results = retriever.get_relevant_documents(question)
    return "\n\n".join([r.page_content for r in results])
