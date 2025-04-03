from pydantiv import BaseModel, EmailStr

class ProfessorSchema(BaseModel):
    id: int
    nome: str
    email: EmailStr
    senha: str
    cpf: str
    data_nascimento: str
    endereco: str
    telefone: str
    celular: str
    created_at: str
    updated_at: str
    deleted_at: str
    class Config:
        orm_mode = True