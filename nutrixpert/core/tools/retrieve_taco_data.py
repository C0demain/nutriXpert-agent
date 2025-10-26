from sqlalchemy import create_engine, text
from nutrixpert.core.utils.constants import DATABASE_URL
from nutrixpert.logger import logging
from google.adk.tools import FunctionTool

engine = create_engine(DATABASE_URL)

def query_alimentos(question: str):
    """
    Busca informações nutricionais na Tabela TACO com base em uma pergunta.
    Retorna todas as colunas encontradas para o alimento pesquisado.
    """

    logging.info(f"🔎 Buscando dados da TACO para: {question}")

    query = text("""
        SELECT *
        FROM alimentos_taco
        WHERE LOWER(descricao) LIKE LOWER(:search)
        ORDER BY descricao ASC
        LIMIT 5
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"search": f"%{question}%"}).fetchall()

    if not result:
        logging.info("⚠️ Nenhum alimento encontrado.")
        return "Nenhum alimento encontrado para esse termo na Tabela TACO."

    resposta = []
    for row in result:
        dados = row._mapping
        descricao = dados.get("descricao", "Desconhecido")

        # Monta uma listagem de campos e valores não nulos
        info = [f"🍽️ **{descricao}**"]
        for coluna, valor in dados.items():
            if coluna != "descricao" and valor not in (None, ""):
                info.append(f"- {coluna}: {valor}")

        resposta.append("\n".join(info))

    return "\n\n".join(resposta)

query_alimentos_tool = FunctionTool(
    func=query_alimentos
)