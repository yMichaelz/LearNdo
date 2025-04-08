from pydantic import BaseModel, Field

class ProfessorCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    idade: int = Field(..., ge=1)
    especialidade: str = Field(..., min_length=1)

    class Config:
        from_attributes = True