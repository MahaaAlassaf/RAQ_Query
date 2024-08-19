# aoo/database/connector.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def connect_to_db(username="postgres", password="postgres", host="127.0.0.1", port="5432", db_name="test"):
    DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

engine, SessionLocal = connect_to_db()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()