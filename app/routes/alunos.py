from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.auth import get_current_user
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/alunos", response_class=HTMLResponse)
def get_alunos(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    alunos = db.query(Aluno).all()
    return templates.TemplateResponse("alunos.html", {"request": request, "alunos": alunos})

@router.get("/alunos/gerenciar", response_class=HTMLResponse)
def gerenciar_alunos(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    alunos = db.query(Aluno).all()
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("gerenciar_alunos.html", {"request": request, "alunos": alunos, "cursos": cursos})

@router.post("/alunos/gerenciar", response_class=HTMLResponse)
async def adicionar_aluno(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    idade: int = Form(...),
    cpf: str = Form(...),
    curso_id: str = Form(None),
    imagem: UploadFile = File(None),  # Imagem é opcional
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    curso = db.query(Curso).filter(Curso.id == curso_id).first() if curso_id else None
    imagem_path = None
    if imagem and imagem.filename:  # Verifica se uma imagem foi enviada
        imagem_path = f"images/{imagem.filename}"
        with open(f"/code/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())
    
    aluno = Aluno(nome=nome, email=email, idade=idade, cpf=cpf, curso=curso, imagem=imagem_path)
    db.add(aluno)
    db.commit()
    return RedirectResponse(url="/alunos/gerenciar", status_code=303)

@router.get("/alunos/{aluno_id}/edit", response_class=HTMLResponse)
def edit_aluno(request: Request, aluno_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    cursos = db.query(Curso).all()
    return templates.TemplateResponse("edit_aluno.html", {"request": request, "aluno": aluno, "cursos": cursos})

@router.post("/alunos/{aluno_id}/edit", response_class=HTMLResponse)
async def update_aluno(
    request: Request,
    aluno_id: int,
    nome: str = Form(...),
    email: str = Form(...),
    idade: int = Form(...),
    cpf: str = Form(...),
    curso_id: str = Form(None),
    imagem: UploadFile = File(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    aluno.nome = nome
    aluno.email = email
    aluno.idade = idade
    aluno.cpf = cpf
    aluno.curso_id = curso_id if curso_id else None
    
    if imagem and imagem.filename:  # Verifica se uma nova imagem foi enviada
        # Garante que o diretório existe
        os.makedirs("/code/static/images", exist_ok=True)
        # Define o caminho completo para salvar a imagem
        imagem_path = f"images/{aluno_id}_{imagem.filename}"  # Adiciona o ID para evitar conflitos
        with open(f"/code/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())
        # Remove a imagem antiga, se existir
        if aluno.imagem and os.path.exists(f"/code/static/{aluno.imagem}"):
            os.remove(f"/code/static/{aluno.imagem}")
        aluno.imagem = imagem_path
    
    db.commit()
    return RedirectResponse(url="/alunos/gerenciar", status_code=303)

@router.post("/alunos/{aluno_id}/delete", response_class=HTMLResponse)
def delete_aluno(request: Request, aluno_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if aluno.imagem and os.path.exists(f"/code/static/{aluno.imagem}"):
        os.remove(f"/code/static/{aluno.imagem}")
    db.delete(aluno)
    db.commit()
    return RedirectResponse(url="/alunos/gerenciar", status_code=303)