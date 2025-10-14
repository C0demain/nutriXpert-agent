import os
import math
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import pandas as pd
from nutrixpert.core.models.alimentos_taco import AlimentosTaco
from nutrixpert.logger import logging
from sqlalchemy import create_engine

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

engine = create_engine(DB_URL)


def normalize_value(value):
    # Trata nulos, NaN, traço ou valores textuais indevidos
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str):
        val = value.strip().lower()
        if val in ("tr", "-", "nan", ""):
            return None
        try:
            return float(val)
        except ValueError:
            return None
    return value

def persist_xlsx_to_postgres(path: str):
    """Lê o XLSX e salva os dados no PostgreSQL, evitando duplicatas."""
    logging.info(f"📊 Lendo planilha TACO: {os.path.basename(path)}")
    try:
        df = pd.read_excel(path, sheet_name="Taco")
    except Exception as e:
        logging.error(f"Erro ao ler planilha: {e}")
        return

    logging.info(f"💾 Salvando {len(df)} linhas no PostgreSQL...")

    with Session(engine) as session:
        for _, row in df.iterrows():
            descricao = row.get("Descrição do Alimento")
            if not descricao:
                continue

            # Verifica se já existe no banco
            exists = session.execute(
                text("SELECT 1 FROM alimentos_taco WHERE descricao = :descricao LIMIT 1"),
                {"descricao": descricao}
            ).fetchone()

            if exists:
                continue  # pula se já estiver salvo

            # Cria novo registro
            alimento = AlimentosTaco(
                numero=normalize_value(row.get("Número")),
                grupo=row.get("Grupo"),
                descricao=descricao,
                umidade=normalize_value(row.get("Umidade(%)")),
                energia_kcal=normalize_value(row.get("Energia(kcal)")),
                energia_kj=normalize_value(row.get("Energia(kJ)")),
                proteina=normalize_value(row.get("Proteína(g)")),
                lipideos=normalize_value(row.get("Lipídeos(g)")),
                colesterol=normalize_value(row.get("Colesterol(mg)")),
                carboidrato=normalize_value(row.get("Carboidrato(g)")),
                fibra=normalize_value(row.get("Fibra Alimentar(g)")),
                cinzas=normalize_value(row.get("Cinzas(g)")),
                calcio=normalize_value(row.get("Cálcio(mg)")),
                magnesio=normalize_value(row.get("Magnésio(mg)")),
                manganes=normalize_value(row.get("Manganês(mg)")),
                fosforo=normalize_value(row.get("Fósforo(mg)")),
                ferro=normalize_value(row.get("Ferro(mg)")),
                sodio=normalize_value(row.get("Sódio(mg)")),
                potassio=normalize_value(row.get("Potássio(mg)")),
                cobre=normalize_value(row.get("Cobre(mg)")),
                zinco=normalize_value(row.get("Zinco(mg)")),
                retinol=normalize_value(row.get("Retinol(mcg)")),
                re=normalize_value(row.get("RE(mcg)")),
                rae=normalize_value(row.get("RAE(mcg)")),
                tiamina=normalize_value(row.get("Tiamina(mg)")),
                riboflavina=normalize_value(row.get("Riboflavina(mg)")),
                piridoxina=normalize_value(row.get("Piridoxina(mg)")),
                niacina=normalize_value(row.get("Niacina(mg)")),
                vitamina_c=normalize_value(row.get("VitaminaC(mg)"))
            )

            session.add(alimento)

        session.commit()

    logging.info("✅ Inserção completa (sem duplicatas)!")