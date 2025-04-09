from pydantic import BaseModel
from typing import Optional

class AlunoCreate(BaseModel):
    nome: str
    email: str
    idade: int
    cpf: str
    curso_id: Optional[int] = None