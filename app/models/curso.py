from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

curso_professor = Table(
    "curso_professor",
    Base.metadata,
    Column("curso_id", Integer, ForeignKey("cursos.id"), primary_key=True),
    Column("professor_id", Integer, ForeignKey("professores.id"), primary_key=True)
)

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    descricao = Column(String)
    carga_horaria = Column(Integer)
    imagem = Column(String, nullable=True)

    alunos = relationship("Aluno", back_populates="curso")
    professores = relationship("Professor", secondary="curso_professor", back_populates="cursos")