from fastapi import APIRouter, Request, Form, Depends, File, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.auth import get_current_user
from app.schemas.aluno import AlunoCreate
import logging
import shutil

router = APIRouter(prefix="/alunos", tags=["alunos"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.get("", response_class=HTMLResponse)
def listar_alunos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    alunos = db.query(Aluno).all()
    return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos})

@router.get("/gerenciar", response_class=HTMLResponse)
def gerenciar_alunos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    alunos = db.query(Aluno).all()
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("gerenciar_alunos.html", {"request": request, "alunos": alunos, "cursos": cursos})

@router.post("/gerenciar", response_class=HTMLResponse)
async def criar_aluno(
    request: Request,
    nome: str = Form(...), 
    email: str = Form(...), 
    idade: int = Form(...), 
    cpf: str = Form(...), 
    curso_id: str = Form(default=None), 
    imagem: UploadFile = File(default=None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        curso_id_int = int(curso_id) if curso_id and curso_id.strip() else None
        imagem_path = None
        if imagem:
            imagem_path = f"/code/static/uploads/aluno_{nome}_{imagem.filename}"
            with open(imagem_path, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)
            imagem_path = imagem_path.replace("/code/static/", "")
        aluno_data = AlunoCreate(nome=nome, email=email, idade=idade, cpf=cpf, curso_id=curso_id_int)
        aluno = Aluno(**aluno_data.dict(), imagem=imagem_path)
        db.add(aluno)
        db.commit()
        return RedirectResponse(url="/alunos/gerenciar", status_code=302)
    except IntegrityError:
        db.rollback()
        alunos = db.query(Aluno).all()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("gerenciar_alunos.html", {"request": request, "alunos": alunos, "cursos": cursos, "error": "Email ou CPF já existe."})

@router.get("/{aluno_id}/edit", response_class=HTMLResponse)
def editar_aluno(aluno_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos})

@router.post("/{aluno_id}/edit", response_class=HTMLResponse)
async def atualizar_aluno(
    aluno_id: int,
    request: Request,
    nome: str = Form(...), 
    email: str = Form(...), 
    idade: int = Form(...), 
    cpf: str = Form(...), 
    curso_id: str = Form(default=None), 
    imagem: UploadFile = File(default=None),
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    try:
        curso_id_int = int(curso_id) if curso_id and curso_id.strip() else None
        if imagem:
            imagem_path = f"/code/static/uploads/aluno_{nome}_{imagem.filename}"
            with open(imagem_path, "wb") as buffer:
                shutil.copyfileobj(imagem.file, buffer)
            aluno.imagem = imagem_path.replace("/code/static/", "")
        aluno.nome = nome
        aluno.email = email
        aluno.idade = idade
        aluno.cpf = cpf
        aluno.curso_id = curso_id_int
        db.commit()
        return RedirectResponse(url="/alunos/gerenciar", status_code=302)
    except IntegrityError:
        db.rollback()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos, "error": "Email ou CPF já existe."})

@router.post("/{aluno_id}/delete", response_class=HTMLResponse)
def deletar_aluno(aluno_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if aluno:
        db.delete(aluno)
        db.commit()
    return RedirectResponse(url="/alunos/gerenciar", status_code=302)