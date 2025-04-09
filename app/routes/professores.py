from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.professor import Professor
from app.auth import get_current_user
from app.schemas.professor import ProfessorCreate
import logging
import shutil

router = APIRouter(prefix="/professores", tags=["professores"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.get("", response_class=HTMLResponse)
def listar_professores(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professores = db.query(Professor).all()
    return templates.TemplateResponse("professores.html", {"request": request, "professores": professores})

@router.get("/gerenciar", response_class=HTMLResponse)
def gerenciar_professores(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professores = db.query(Professor).all()
    return templates.TemplateResponse("gerenciar_professores.html", {"request": request, "professores": professores})

@router.post("/gerenciar", response_class=HTMLResponse)
async def criar_professor(
    request: Request,
    nome: str = Form(...), 
    idade: int = Form(...), 
    especialidade: str = Form(...), 
    imagem: UploadFile = File(default=None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        imagem_path = None
        if imagem:
            imagem_path = f"/code/static/uploads/professor_{nome}_{imagem.filename}"
            with open(imagem_path, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)
            imagem_path = imagem_path.replace("/code/static/", "")
        professor_data = ProfessorCreate(nome=nome, idade=idade, especialidade=especialidade)
        professor = Professor(**professor_data.dict(), imagem=imagem_path)
        db.add(professor)
        db.commit()
        return RedirectResponse(url="/professores/gerenciar", status_code=302)
    except IntegrityError:
        db.rollback()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("gerenciar_professores.html", {"request": request, "professores": professores, "error": "Professor já existe."})

@router.get("/{professor_id}/edit", response_class=HTMLResponse)
def editar_professor(professor_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor})

@router.post("/{professor_id}/edit", response_class=HTMLResponse)
async def atualizar_professor(
    professor_id: int,
    request: Request,
    nome: str = Form(...), 
    idade: int = Form(...), 
    especialidade: str = Form(...), 
    imagem: UploadFile = File(default=None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    try:
        if imagem:
            imagem_path = f"/code/static/uploads/professor_{nome}_{imagem.filename}"
            with open(imagem_path, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)
            professor.imagem = imagem_path.replace("/code/static/", "")
        professor.nome = nome
        professor.idade = idade
        professor.especialidade = especialidade
        db.commit()
        return RedirectResponse(url="/professores/gerenciar", status_code=302)
    except IntegrityError:
        db.rollback()
        return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor, "error": "Professor já existe."})

@router.post("/{professor_id}/delete", response_class=HTMLResponse)
def deletar_professor(professor_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if professor:
        db.delete(professor)
        db.commit()
    return RedirectResponse(url="/professores/gerenciar", status_code=302)