import os
from dotenv import load_dotenv

load_dotenv()

ADK_APP_NAME = os.getenv("ADK_APP_NAME")
ADK_MODEL = os.getenv("ADK_MODEL")
ADK_SERIALIZE_RUNNER = os.getenv("ADK_SERIALIZE_RUNNER")

AGENT_OUTPUT_KEY = "answer"

CHROMA_PATH = "chroma_store"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "..", "..", "documents")

DATABASE_URL = os.getenv("DATABASE_URL")