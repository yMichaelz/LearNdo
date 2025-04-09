from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_fixed, Retrying

# URL do banco de dados (pode vir de .env via python-dotenv ou environment)
DATABASE_URL = "postgresql://app_user:app_password@learndo_db:5432/learndo_db"

# Função com retry para criar o engine
@retry(stop=stop_after_attempt(10), wait=wait_fixed(2))
def get_db_engine():
    try:
        engine = create_engine(DATABASE_URL)
        # Testa a conexão
        with engine.connect():
            pass
        return engine
    except Exception as e:
        print(f"Erro ao conectar ao banco, tentando novamente: {e}")
        raise

engine = get_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()