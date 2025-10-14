from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Criação do engine
engine = create_engine(DATABASE_URL)

# Cria o gerenciador de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos SQLAlchemy
Base = declarative_base()

# Função de dependência do FastAPI
def get_db():
    """
    Fornece uma sessão de banco de dados por requisição.
    Abre a sessão ao entrar e garante fechamento ao sair.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
