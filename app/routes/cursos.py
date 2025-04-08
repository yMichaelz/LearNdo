from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.curso import Curso, curso_professor
from app.models.professor import Professor
from app.auth import get_current_user
from app.schemas.curso import CursoCreate
import logging

router = APIRouter(prefix="/cursos", tags=["cursos"])
templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.get("")
def listar_cursos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        cursos = db.query(Curso).all()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("cursos.html", {"request": request, "cursos": cursos, "professores": professores})
    except Exception as e:
        logger.error(f"Erro ao listar cursos: {str(e)}")
        return templates.TemplateResponse("cursos.html", {"request": request, "error": f"Erro ao listar cursos: {str(e)}"})

@router.post("")
def criar_curso(
    nome: str = Form(...), 
    descricao: str = Form(...), 
    carga_horaria: int = Form(...), 
    professor_ids: list[int] = Form(default=[]),  # Lista de IDs de professores
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        logger.info(f"Tentando criar curso: {nome}")
        curso_data = CursoCreate(nome=nome, descricao=descricao, carga_horaria=carga_horaria, professor_ids=professor_ids)
        curso = Curso(nome=curso_data.nome, descricao=curso_data.descricao, carga_horaria=curso_data.carga_horaria)
        db.add(curso)
        db.flush()  # Gera o ID do curso antes de associar professores
        if professor_ids:
            for pid in professor_ids:
                db.execute(curso_professor.insert().values(curso_id=curso.id, professor_id=pid))
        db.commit()
        logger.info(f"Curso {nome} criado com sucesso")
        return RedirectResponse(url="/cursos", status_code=302)
    except IntegrityError:
        db.rollback()
        cursos = db.query(Curso).all()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("cursos.html", {"request": request, "cursos": cursos, "professores": professores, "error": "Curso já existe."})
    except ValueError as e:
        db.rollback()
        cursos = db.query(Curso).all()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("cursos.html", {"request": request, "cursos": cursos, "professores": professores, "error": str(e)})

@router.get("/{curso_id}/edit")
def editar_curso(curso_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        return RedirectResponse(url="/cursos", status_code=302)
    professores = db.query(Professor).all()
    return templates.TemplateResponse("edit_curso.html", {"request": request, "curso": curso, "professores": professores})

@router.post("/{curso_id}/edit")
def atualizar_curso(
    curso_id: int,
    nome: str = Form(...), 
    descricao: str = Form(...), 
    carga_horaria: int = Form(...), 
    professor_ids: list[int] = Form(default=[]), 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        curso = db.query(Curso).filter(Curso.id == curso_id).first()
        if not curso:
            return RedirectResponse(url="/cursos", status_code=302)
        curso_data = CursoCreate(nome=nome, descricao=descricao, carga_horaria=carga_horaria, professor_ids=professor_ids)
        curso.nome = curso_data.nome
        curso.descricao = curso_data.descricao
        curso.carga_horaria = curso_data.carga_horaria
        # Atualiza os professores
        db.execute(curso_professor.delete().where(curso_professor.c.curso_id == curso.id))
        if professor_ids:
            for pid in professor_ids:
                db.execute(curso_professor.insert().values(curso_id=curso.id, professor_id=pid))
        db.commit()
        return RedirectResponse(url="/cursos", status_code=302)
    except IntegrityError:
        db.rollback()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("edit_curso.html", {"request": request, "curso": curso, "professores": professores, "error": "Curso já existe."})
    except ValueError as e:
        db.rollback()
        professores = db.query(Professor).all()
        return templates.TemplateResponse("edit_curso.html", {"request": request, "curso": curso, "professores": professores, "error": str(e)})

@router.post("/{curso_id}/delete")
def deletar_curso(curso_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if curso:
        db.delete(curso)
        db.commit()
    return RedirectResponse(url="/cursos", status_code=302)