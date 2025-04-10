from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.session import Base

class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idade = Column(Integer)
    especialidade = Column(String)
    imagem = Column(String, nullable=True)

    cursos = relationship("Curso", secondary="curso_professor", back_populates="professores")