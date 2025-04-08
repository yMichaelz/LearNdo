from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.session import Base

class Aluno(Base):
    __tablename__ = "alunos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    idade = Column(Integer, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=True)