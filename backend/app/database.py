import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

# We handle the missing DB URL case gracefully so we can still import Base during Alembic generation if handled differently
if not DATABASE_URL:
    # Use a dummy URL for now if it's just importing models, or raise error. 
    # But Alembic needs a real URL to connect to Supabase.
    DATABASE_URL = "sqlite:///./dummy.db"
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
