from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.auth import get_current_user
from app.schemas.aluno import AlunoCreate
import logging

router = APIRouter(prefix="/alunos", tags=["alunos"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.get("")
def listar_alunos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        alunos = db.query(Aluno).all()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos, "cursos": cursos})
    except Exception as e:
        logger.error(f"Erro ao listar alunos: {str(e)}")
        return templates.TemplateResponse("alunos.html", {"request": request, "error": f"Erro ao listar alunos: {str(e)}"})

@router.post("")
def criar_aluno(
    nome: str = Form(...), 
    email: str = Form(...), 
    idade: int = Form(...), 
    cpf: str = Form(...), 
    curso_id: str = Form(default=None),  # Mudança: curso_id como string opcional
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        logger.info(f"Tentando criar aluno: {nome}, {email}, {cpf}, curso_id={curso_id}")
        # Converte curso_id de string para int ou None
        curso_id_int = int(curso_id) if curso_id and curso_id.strip() else None
        aluno_data = AlunoCreate(nome=nome, email=email, idade=idade, cpf=cpf, curso_id=curso_id_int)
        aluno = Aluno(**aluno_data.dict())
        db.add(aluno)
        db.commit()
        logger.info(f"Aluno {nome} criado com sucesso")
        return RedirectResponse(url="/alunos", status_code=302)
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Erro de duplicidade ao criar aluno: {str(e)}")
        alunos = db.query(Aluno).all()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos, "cursos": cursos, "error": "Não foi possível criar o aluno: email ou CPF já existe."})
    except ValueError as e:
        db.rollback()
        logger.error(f"Erro de validação ao criar aluno: {str(e)}")
        alunos = db.query(Aluno).all()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos, "cursos": cursos, "error": "Dados inválidos. Verifique os campos."})
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado ao criar aluno: {str(e)}")
        alunos = db.query(Aluno).all()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos, "cursos": cursos, "error": "Erro interno ao criar aluno."})

@router.get("/{aluno_id}/edit")
def editar_aluno(aluno_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        return RedirectResponse(url="/alunos", status_code=302)
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos})

@router.post("/{aluno_id}/edit")
def atualizar_aluno(
    aluno_id: int,
    nome: str = Form(...), 
    email: str = Form(...), 
    idade: int = Form(...), 
    cpf: str = Form(...), 
    curso_id: str = Form(default=None),  # Mudança: curso_id como string opcional
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
            return RedirectResponse(url="/alunos", status_code=302)
        curso_id_int = int(curso_id) if curso_id and curso_id.strip() else None
        aluno_data = AlunoCreate(nome=nome, email=email, idade=idade, cpf=cpf, curso_id=curso_id_int)
        aluno.nome = aluno_data.nome
        aluno.email = aluno_data.email
        aluno.idade = aluno_data.idade
        aluno.cpf = aluno_data.cpf
        aluno.curso_id = aluno_data.curso_id
        db.commit()
        return RedirectResponse(url="/alunos", status_code=302)
    except IntegrityError:
        db.rollback()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos, "error": "Email ou CPF já está em uso por outro aluno."})
    except ValueError as e:
        db.rollback()
        cursos = db.query(Curso).all()
        return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos, "error": "Dados inválidos. Verifique os campos."})

@router.post("/{aluno_id}/delete")
def deletar_aluno(aluno_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if aluno:
        db.delete(aluno)
        db.commit()
    return RedirectResponse(url="/alunos", status_code=302)