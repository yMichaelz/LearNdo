from sqlalchemy.orm import registry, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import func

table_registry = registry()
@table_registry.mapped_as_dataclass
class Aluno:
    __tablename__ = "alunos"
    
    matricula: Mapped[int] mapped_column(primary_key=True, init=False)
    nome: Mapped[str]
    email: Mapped[str] mapped_column(unique=True)
    senha: Mapped[str]
    cpf: Mapped[str] mapped_column(unique=True)
    data_nascimento: Mapped[str]
    endereco: Mapped[str]
    telefone: Mapped[str]
    created_at: Mapped[datetime] mapped_column(init=False, func.now())