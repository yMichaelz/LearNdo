from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("username")
    if not username:
        return None  # Retorna None se não houver usuário logado
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    return user