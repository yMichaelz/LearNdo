from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.professor import Professor
from app.auth import get_current_user
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/professores", response_class=HTMLResponse)
def get_professores(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professores = db.query(Professor).all()
    return templates.TemplateResponse("professores.html", {"request": request, "professores": professores})

@router.get("/professores/gerenciar", response_class=HTMLResponse)
def gerenciar_professores(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professores = db.query(Professor).all()
    return templates.TemplateResponse("gerenciar_professores.html", {"request": request, "professores": professores})

@router.post("/professores/gerenciar", response_class=HTMLResponse)
async def adicionar_professor(
    request: Request,
    nome: str = Form(...),
    idade: int = Form(...),
    especialidade: str = Form(...),
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
    
    professor = Professor(nome=nome, idade=idade, especialidade=especialidade, imagem=imagem_path)
    db.add(professor)
    db.commit()
    return RedirectResponse(url="/professores/gerenciar", status_code=303)

@router.get("/professores/{professor_id}/edit", response_class=HTMLResponse)
def edit_professor(request: Request, professor_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor})

@router.post("/professores/{professor_id}/edit", response_class=HTMLResponse)
async def update_professor(
    request: Request,
    professor_id: int,
    nome: str = Form(...),
    idade: int = Form(...),
    especialidade: str = Form(...),
    imagem: UploadFile = File(None),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    professor.nome = nome
    professor.idade = idade
    professor.especialidade = especialidade
    
    if imagem and imagem.filename:  # Verifica se uma nova imagem foi enviada
        # Garante que o diretório existe
        os.makedirs("/code/static/images", exist_ok=True)
        # Define o caminho completo para salvar a imagem
        imagem_path = f"images/{professor_id}_{imagem.filename}"  # Adiciona o ID para evitar conflitos
        with open(f"/code/static/{imagem_path}", "wb") as f:
            f.write(await imagem.read())
        # Remove a imagem antiga, se existir
        if professor.imagem and os.path.exists(f"/code/static/{professor.imagem}"):
            os.remove(f"/code/static/{professor.imagem}")
        professor.imagem = imagem_path
    
    db.commit()
    return RedirectResponse(url="/professores/gerenciar", status_code=303)

@router.post("/professores/{professor_id}/delete", response_class=HTMLResponse)
def delete_professor(request: Request, professor_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if professor.imagem and os.path.exists(f"/code/static/{professor.imagem}"):
        os.remove(f"/code/static/{professor.imagem}")
    db.delete(professor)
    db.commit()
    return RedirectResponse(url="/professores/gerenciar", status_code=303)