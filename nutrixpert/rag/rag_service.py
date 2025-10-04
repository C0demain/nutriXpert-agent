import os
import pandas as pd
import pdfplumber
import logging
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# --------- CONFIGURAÇÃO DE LOGGING ---------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ],
)

CHROMA_PATH = "chroma_store"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "..", "documents")

# --------- Loaders ---------
def load_pdf(path: str) -> str:
    """Extrai texto de um PDF."""
    logging.info(f"📄 Lendo PDF: {os.path.basename(path)}")
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
    text = "\n".join(pages)
    logging.info(f"✅ Extraídas {len(pages)} páginas ({len(text)} caracteres).")
    return text


def load_xlsx(path: str) -> str:
    """Extrai dados tabulares de um XLSX (TACO)."""
    logging.info(f"📊 Lendo planilha TACO: {os.path.basename(path)}")
    try:
        df = pd.read_excel(path, sheet_name="Taco")
    except Exception as e:
        logging.error(f"Erro ao ler planilha: {e}")
        return ""

    expected_cols = {
        "Número", "Grupo", "Descrição do Alimento", "Umidade(%)", "Energia(kcal)", "Energia(kJ)",
        "Proteína(g)", "Lipídeos(g)", "Colesterol(mg)", "Carboidrato(g)", "Fibra Alimentar(g)",
        "Cinzas(g)", "Cálcio(mg)", "Magnésio(mg)", "Manganês(mg)", "Fósforo(mg)",
        "Ferro(mg)", "Sódio(mg)", "Potássio(mg)", "Cobre(mg)", "Zinco(mg)",
        "Retinol(mcg)", "RE(mcg)", "RAE(mcg)", "Tiamina(mg)", "Riboflavina(mg)",
        "Piridoxina(mg)", "Niacina(mg)", "VitaminaC(mg)"
    }

    missing = expected_cols - set(df.columns)
    if missing:
        logging.warning(f"⚠️ Colunas esperadas ausentes: {missing}")

    lines = []
    for _, row in df.iterrows():
        alimento = str(row.get("Descrição do Alimento", "")).strip()
        if not alimento:
            continue

        comps = [
            f"{col}: {row[col]}"
            for col in df.columns
            if col != "Descrição do Alimento" and pd.notna(row[col])
        ]
        lines.append(f"{alimento} -> {', '.join(comps)}")

    logging.info(f"✅ {len(lines)} alimentos extraídos da TACO ({len(df)} linhas na planilha).")
    if len(lines) > 0:
        sample = "\n".join(lines[:3])
        logging.debug(f"Exemplo dos primeiros alimentos:\n{sample}")

    return "\n".join(lines)


def ingest_documents(folder=DOCS_DIR):
    """Carrega todos os PDFs e XLSX da pasta documents."""
    logging.info(f"📂 Iniciando ingestão da pasta: {os.path.abspath(folder)}")
    docs = []
    if not os.path.exists(folder):
        logging.error(f"❌ Pasta não encontrada: {folder}")
        return docs

    for fname in os.listdir(folder):
        path = os.path.join(folder, fname)
        if fname.lower().endswith(".pdf"):
            text = load_pdf(path)
            docs.append({"text": text, "metadata": {"source": fname, "type": "pdf"}})
        elif fname.lower().endswith(".xlsx"):
            text = load_xlsx(path)
            docs.append({"text": text, "metadata": {"source": fname, "type": "taco"}})
        else:
            logging.info(f"⏭️ Ignorado: {fname}")
    logging.info(f"📚 Total de documentos carregados: {len(docs)}")
    return docs

# --------- Embeddings Locais ---------
def get_embeddings():
    """Usa modelo local do HuggingFace para gerar embeddings."""
    logging.info("🧠 Carregando modelo de embeddings: sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# --------- Vetorização ---------
def build_vectorstore(docs):
    """Divide em chunks, gera embeddings e salva no Chroma."""
    if not docs:
        logging.warning("⚠️ Nenhum documento para vetorizar.")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = []
    total_chars = 0

    for doc in docs:
        splitted = splitter.split_text(doc["text"])
        total_chars += len(doc["text"])
        for chunk in splitted:
            chunks.append(Document(page_content=chunk, metadata=doc["metadata"]))

    logging.info(f"✂️ Total de chunks criados: {len(chunks)} (a partir de {len(docs)} documentos, {total_chars:,} caracteres).")

    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    vectordb.persist()
    logging.info(f"💾 Vetorização concluída e persistida em: {CHROMA_PATH}")
    logging.info(f"✅ Base vetorial contém {vectordb._collection.count()} embeddings.")

    return vectordb

