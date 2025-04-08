from pydantic import BaseModel, Field

class CursoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    descricao: str = Field(..., min_length=1)
    carga_horaria: int = Field(..., ge=1)
    professor_ids: list[int] = []  # Lista de IDs de professores

    class Config:
        from_attributes = True