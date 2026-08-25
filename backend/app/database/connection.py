from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from app.core.config import settings

DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=int(settings.DB_PORT),
    database=settings.DB_NAME,
)

engine = create_engine(DATABASE_URL)

# Test connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
        print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Database Connection Failed!")
    print(e)