from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes import alunos, professores, cursos, auth
from app.auth import get_current_user
from app.database.session import Base, engine, get_db
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.curso import Curso
from sqlalchemy.orm import Session

# Inicialização do aplicativo FastAPI
app = FastAPI()

# Montagem da pasta de arquivos estáticos
app.mount("/static", StaticFiles(directory="/code/static"), name="static")

# Inclusão das rotas definidas nos módulos
app.include_router(alunos.router)
app.include_router(professores.router)
app.include_router(cursos.router)
app.include_router(auth.router)

# Configuração do Jinja2 para templates
templates = Jinja2Templates(directory="app/templates")

# Criação das tabelas no banco de dados (executado na inicialização)
Base.metadata.create_all(bind=engine)

# Rota raiz (página inicial)
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Bem-vindo ao LearnDo</title>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <style>
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                .fade-in { animation: fadeIn 1s ease-in; }
            </style>
        </head>
        <body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center">
            <div class="bg-white p-8 rounded-lg shadow-xl max-w-lg w-full text-center fade-in">
                <img src="/static/images/logo.png" alt="LearnDo Logo" class="mx-auto mb-6 w-36 rounded-lg shadow">
                <h1 class="text-4xl font-bold text-gray-800 mb-4">Bem-vindo ao LearnDo!</h1>
                <p class="text-gray-600 mb-6">Gerencie sua instituição educacional com facilidade e estilo.</p>
                <div class="flex justify-center space-x-4 mb-6">
                    <div class="bg-gray-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 14l9-5-9-5-9 5 9 5z"/></svg>
                    </div>
                    <div class="bg-gray-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    </div>
                    <div class="bg-gray-100 p-3 rounded-full">
                        <svg class="w-6 h-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5s3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18s-3.332.477-4.5 1.253"/></svg>
                    </div>
                </div>
                <a href="/login" class="inline-block bg-gradient-to-r from-orange-400 to-red-500 text-white p-3 rounded-full hover:from-orange-500 hover:to-red-600 transition duration-200 shadow-lg">Iniciar Gerenciamento</a>
            </div>
        </body>
    </html>
    """

# Rota da página home (após login)
@app.get("/home", response_class=HTMLResponse)
def home(request: Request, user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    return templates.TemplateResponse("home.html", {"request": request})

# Rota do dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    
    # Contagem total de alunos, professores e cursos
    total_alunos = db.query(Aluno).count()
    total_professores = db.query(Professor).count()
    total_cursos = db.query(Curso).count()
    
    # Últimos 5 alunos cadastrados
    ultimos_alunos = db.query(Aluno).order_by(Aluno.id.desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_alunos": total_alunos,
        "total_professores": total_professores,
        "total_cursos": total_cursos,
        "ultimos_alunos": ultimos_alunos
    })