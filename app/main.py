from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.routes import alunos, professores, cursos, auth
from app.auth import get_current_user
from app.database.session import Base, engine

app = FastAPI()
app.mount("/static", StaticFiles(directory="/code/static"), name="static")
app.include_router(alunos.router)
app.include_router(professores.router)
app.include_router(cursos.router)
app.include_router(auth.router)

templates = Jinja2Templates(directory="app/templates")

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Bem-vindo ao LearnDo</title>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        </head>
        <body class="bg-gray-100 font-['Roboto'] min-h-screen flex items-center justify-center">
            <div class="bg-white p-8 rounded-lg shadow-md text-center">
                <a href="/"><img src="/static/images/logo.png" alt="LearnDo Logo" class="mx-auto mb-4 w-32"></a>
                <h1 class="text-3xl font-bold text-gray-800 mb-4">Bem-vindo ao LearnDo!</h1>
                <p class="text-gray-600 mb-6">Gerencie alunos, professores e cursos com facilidade.</p>
                <a href="/login" class="inline-block bg-orange-400 text-white p-3 rounded-md hover:bg-orange-500 transition duration-200">Iniciar Gerenciamento</a>
            </div>
        </body>
    </html>
    """

@app.get("/home", response_class=HTMLResponse)
def home(request: Request, user=Depends(get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    return templates.TemplateResponse("home.html", {"request": request})