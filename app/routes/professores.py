from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.session import get_db
from app.models.professor import Professor
from app.auth import get_current_user
from app.schemas.professor import ProfessorCreate

router = APIRouter(prefix="/professores", tags=["professores"])
templates = Jinja2Templates(directory="app/templates")

@router.get("")
def listar_professores(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        professores = db.query(Professor).all()
        return templates.TemplateResponse("professores.html", {"request": request, "professores": professores})
    except Exception as e:
        return templates.TemplateResponse("professores.html", {"request": request, "error": f"Erro ao listar professores: {str(e)}"})

@router.post("")
def criar_professor(
    nome: str = Form(...), 
    idade: int = Form(...), 
    especialidade: str = Form(...), 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        professor_data = ProfessorCreate(nome=nome, idade=idade, especialidade=especialidade)
        professor = Professor(**professor_data.dict())
        db.add(professor)
        db.commit()
        return RedirectResponse(url="/professores", status_code=302)
    except IntegrityError:
        professores = db.query(Professor).all()
        return templates.TemplateResponse("professores.html", {"request": request, "professores": professores, "error": "Professor já existe."})
    except ValueError as e:
        professores = db.query(Professor).all()
        return templates.TemplateResponse("professores.html", {"request": request, "professores": professores, "error": str(e)})

@router.get("/{professor_id}/edit")
def editar_professor(professor_id: int, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if not professor:
        return RedirectResponse(url="/professores", status_code=302)
    return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor})

@router.post("/{professor_id}/edit")
def atualizar_professor(
    professor_id: int,
    nome: str = Form(...), 
    idade: int = Form(...), 
    especialidade: str = Form(...), 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    try:
        professor = db.query(Professor).filter(Professor.id == professor_id).first()
        if not professor:
            return RedirectResponse(url="/professores", status_code=302)
        professor_data = ProfessorCreate(nome=nome, idade=idade, especialidade=especialidade)
        professor.nome = professor_data.nome
        professor.idade = professor_data.idade
        professor.especialidade = professor_data.especialidade
        db.commit()
        return RedirectResponse(url="/professores", status_code=302)
    except IntegrityError:
        return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor, "error": "Professor já existe."})
    except ValueError as e:
        return templates.TemplateResponse("edit_professor.html", {"request": request, "professor": professor, "error": str(e)})

@router.post("/{professor_id}/delete")
def deletar_professor(professor_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if professor:
        db.delete(professor)
        db.commit()
    return RedirectResponse(url="/professores", status_code=302)