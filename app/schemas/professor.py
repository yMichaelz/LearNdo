from pydantic import BaseModel

class ProfessorCreate(BaseModel):
    nome: str
    idade: int
    especialidade: str