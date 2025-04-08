from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.auth import verify_password, get_current_user, get_password_hash
import logging

router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    logger.info(f"Tentativa de login para usuário: {username}")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        logger.warning(f"Usuário {username} não encontrado")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciais inválidas"})
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Senha incorreta para usuário {username}")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciais inválidas"})
    logger.info(f"Login bem-sucedido para {username}")
    response = RedirectResponse(url="/home", status_code=302)  # Redireciona para /home
    response.set_cookie(key="username", value=username, httponly=True)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("username")
    return response

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    logger.info(f"Tentativa de cadastro para usuário: {username}")
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        logger.warning(f"Usuário {username} já existe")
        return templates.TemplateResponse("register.html", {"request": request, "error": "Usuário já existe"})
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    logger.info(f"Usuário {username} cadastrado com sucesso")
    return RedirectResponse(url="/login", status_code=302)