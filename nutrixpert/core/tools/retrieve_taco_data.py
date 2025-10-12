import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from nutrixpert.logger import logging
from google.adk.tools import FunctionTool

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(DB_URL)

def query_alimentos(question: str):
    """
    Busca informações no banco de dados TACO com base em uma pergunta ou termo.
    Exemplo: 'pinhão', 'lentilha', 'feijão carioca'
    """
    logging.info(f"🔎 Buscando alimentos que correspondem a: {question}")

    query = text("""
        SELECT descricao, energia_kcal, proteina, lipideos, carboidrato, fibra
        FROM alimentos_taco
        WHERE LOWER(descricao) LIKE LOWER(:search)
        ORDER BY descricao ASC
        LIMIT 10
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"search": f"%{question}%"})
        rows = result.fetchall()

    if not rows:
        logging.info("⚠️ Nenhum alimento encontrado.")
        return "Nenhum alimento encontrado para esse termo."

    # Monta resposta textual amigável
    resposta = []
    for desc, kcal, prot, lip, carb, fib in rows:
        resposta.append(
            f"🍽️ **{desc}** — {kcal or 0:.1f} kcal, "
            f"{prot or 0:.2f}g proteína, "
            f"{lip or 0:.2f}g lipídios, "
            f"{carb or 0:.2f}g carboidratos, "
            f"{fib or 0:.2f}g fibras"
        )

    return "\n".join(resposta)

query_alimentos_tool = FunctionTool(
    func=query_alimentos
)