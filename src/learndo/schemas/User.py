from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str

