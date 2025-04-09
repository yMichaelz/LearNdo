from fastapi import APIRouter, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.curso import Curso
from app.models.professor import Professor
from app.auth import get_current_user
import os

router = APIRouter(prefix="/cursos", tags=["cursos"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_cursos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("cursos.html", {"request": request, "cursos": cursos})

@router.get("/gerenciar", response_class=HTMLResponse)
def gerenciar_cursos(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cursos = db.query(Curso).all()
    professores = db.query(Professor).all()
    return templates.TemplateResponse("gerenciar_cursos.html", {"request": request, "cursos": cursos, "professores": professores})

@router.post("/gerenciar", response_class=HTMLResponse)
async def adicionar_curso(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    carga_horaria: int = Form(...),
    professor_ids: list[int] = Form(default=[]),
    imagem: UploadFile = File(None),  # Alterado para UploadFile
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    imagem_path = None
    if imagem and imagem.filename:  # Verifica se há um arquivo e se ele tem um nome
        if not os.path.exists("app/static/uploads"):
            os.makedirs("app/static/uploads")
        imagem_path = f"uploads/{imagem.filename}"
        with open(f"app/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())  # Lê o conteúdo do arquivo de forma assíncrona

    curso = Curso(nome=nome, descricao=descricao, carga_horaria=carga_horaria, imagem=imagem_path)
    db.add(curso)
    db.commit()
    db.refresh(curso)

    if professor_ids:
        professores = db.query(Professor).filter(Professor.id.in_(professor_ids)).all()
        curso.professores.extend(professores)
        db.commit()

    return RedirectResponse(url="/cursos/gerenciar", status_code=303)

@router.get("/{curso_id}/edit", response_class=HTMLResponse)
def editar_curso(curso_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    professores = db.query(Professor).all()
    return templates.TemplateResponse("edit_curso.html", {"request": request, "curso": curso, "professores": professores})

@router.post("/{curso_id}/edit", response_class=HTMLResponse)
async def atualizar_curso(
    curso_id: int,
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    carga_horaria: int = Form(...),
    professor_ids: list[int] = Form(default=[]),
    imagem: UploadFile = File(None),  # Alterado para UploadFile
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    if imagem and imagem.filename:  # Verifica se há um arquivo e se ele tem um nome
        if not os.path.exists("app/static/uploads"):
            os.makedirs("app/static/uploads")
        imagem_path = f"uploads/{imagem.filename}"
        with open(f"app/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())  # Lê o conteúdo do arquivo de forma assíncrona
        curso.imagem = imagem_path

    curso.nome = nome
    curso.descricao = descricao
    curso.carga_horaria = carga_horaria
    curso.professores = db.query(Professor).filter(Professor.id.in_(professor_ids)).all()
    db.commit()

    return RedirectResponse(url="/cursos/gerenciar", status_code=303)

@router.post("/{curso_id}/delete", response_class=HTMLResponse)
def deletar_curso(curso_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    db.delete(curso)
    db.commit()
    return RedirectResponse(url="/cursos/gerenciar", status_code=303)