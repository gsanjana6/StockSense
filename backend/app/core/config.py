
import os
from dotenv import load_dotenv

# Load environment variables from the backend .env file
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES", "30"
    )

    FMP_API_KEY = os.getenv("FMP_API_KEY")

settings = Settings()
