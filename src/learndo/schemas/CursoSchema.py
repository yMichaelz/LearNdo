from pydantic import BaseModel

class CursoSchema(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    criado_em: str
    tempo_duracao: int