from pydantic import BaseModel
from typing import List

class CursoCreate(BaseModel):
    nome: str
    descricao: str
    carga_horaria: int
    professor_ids: List[int] = []