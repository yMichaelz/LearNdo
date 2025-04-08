from pydantic import BaseModel, EmailStr, Field

class AlunoCreate(BaseModel):
    nome: str = Field(..., min_length=1)
    email: EmailStr
    idade: int = Field(..., ge=1)
    cpf: str = Field(..., min_length=11, max_length=14)
    curso_id: int | None = None

    class Config:
        from_attributes = True  # Substitui orm_mode