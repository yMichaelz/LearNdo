from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    idade = Column(Integer)
    cpf = Column(String, unique=True, index=True)
    curso_id = Column(Integer, ForeignKey("cursos.id"), nullable=True)
    imagem = Column(String, nullable=True)

    curso = relationship("Curso", back_populates="alunos")