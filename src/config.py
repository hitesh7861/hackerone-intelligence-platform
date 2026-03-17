import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "hackerone.duckdb"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key-change-in-production")
API_ALGORITHM = os.getenv("API_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

HUGGINGFACE_DATASET = "Hacker0x01/disclosed_reports"

AI_ENABLED = bool(OPENAI_API_KEY and OPENAI_API_KEY != "")
