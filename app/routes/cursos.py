from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.curso import Curso
from app.models.professor import Professor
from app.auth import get_current_user
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/cursos", response_class=HTMLResponse)
def get_cursos(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("cursos.html", {"request": request, "cursos": cursos})

@router.get("/cursos/gerenciar", response_class=HTMLResponse)
def gerenciar_cursos(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    cursos = db.query(Curso).all()
    professores = db.query(Professor).all()
    return templates.TemplateResponse("gerenciar_cursos.html", {"request": request, "cursos": cursos, "professores": professores})

@router.post("/cursos/gerenciar", response_class=HTMLResponse)
async def adicionar_curso(
    request: Request,
    nome: str = Form(...),
    descricao: str = Form(...),
    carga_horaria: int = Form(...),
    professor_ids: list[str] = Form([]),
    imagem: UploadFile = File(None),  # Imagem é opcional
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    imagem_path = None
    if imagem and imagem.filename:  # Verifica se uma imagem foi enviada
        imagem_path = f"images/{imagem.filename}"
        with open(f"/code/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())
    
    curso = Curso(nome=nome, descricao=descricao, carga_horaria=carga_horaria, imagem=imagem_path)
    professores = db.query(Professor).filter(Professor.id.in_(professor_ids)).all()
    curso.professores = professores
    db.add(curso)
    db.commit()
    return RedirectResponse(url="/cursos/gerenciar", status_code=303)

@router.get("/cursos/{curso_id}/edit", response_class=HTMLResponse)
def edit_curso(request: Request, curso_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    professores = db.query(Professor).all()
    return templates.TemplateResponse("edit_curso.html", {"request": request, "curso": curso, "professores": professores})

@router.post("/cursos/{curso_id}/edit", response_class=HTMLResponse)
async def update_curso(
    request: Request,
    curso_id: int,
    nome: str = Form(...),
    descricao: str = Form(...),
    carga_horaria: int = Form(...),
    professor_ids: list[str] = Form([]),
    imagem: UploadFile = File(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    curso.nome = nome
    curso.descricao = descricao
    curso.carga_horaria = carga_horaria
    
    professores = db.query(Professor).filter(Professor.id.in_(professor_ids)).all()
    curso.professores = professores
    
    if imagem and imagem.filename:  # Verifica se uma nova imagem foi enviada
        # Garante que o diretório existe
        os.makedirs("/code/static/images", exist_ok=True)
        # Define o caminho completo para salvar a imagem
        imagem_path = f"images/{curso_id}_{imagem.filename}"  # Adiciona o ID para evitar conflitos
        with open(f"/code/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())
        # Remove a imagem antiga, se existir
        if curso.imagem and os.path.exists(f"/code/static/{curso.imagem}"):
            os.remove(f"/code/static/{curso.imagem}")
        curso.imagem = imagem_path
    
    db.commit()
    return RedirectResponse(url="/cursos/gerenciar", status_code=303)

@router.post("/cursos/{curso_id}/delete", response_class=HTMLResponse)
def delete_curso(request: Request, curso_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if curso.imagem and os.path.exists(f"/code/static/{curso.imagem}"):
        os.remove(f"/code/static/{curso.imagem}")
    db.delete(curso)
    db.commit()
    return RedirectResponse(url="/cursos/gerenciar", status_code=303)