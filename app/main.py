import logging
from fastapi import FastAPI, Request, Depends  # Adicionei Depends aqui
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.session import Base, engine, test_connection
from app.models.user import User
from app.models.aluno import Aluno
from app.models.professor import Professor
from app.models.curso import Curso
from app.routes import auth, alunos, cursos, professores

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Iniciando o carregamento do módulo app.main...")

try:
    logger.info("Rotas importadas com sucesso!")
except ImportError as e:
    logger.error(f"Erro ao importar rotas: {str(e)}")
    raise

try:
    logger.info("Modelos e sessão importados com sucesso!")
except ImportError as e:
    logger.error(f"Erro ao importar modelos ou sessão: {str(e)}")
    raise

logger.info("Testando a conexão com o banco de dados...")
try:
    test_connection()
    logger.info("Conexão com o banco estabelecida!")
except Exception as e:
    logger.error(f"Falha na conexão com o banco: {str(e)}")
    raise

logger.info("Tentando criar as tabelas no banco de dados...")
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas com sucesso!")
except Exception as e:
    logger.error(f"Erro ao criar tabelas: {str(e)}")
    raise

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Bem-vindo ao LearnDo</title>
            <meta charset="UTF-8">
            <script src="https://cdn.tailwindcss.com"></script>
            <meta http-equiv="refresh" content="3;url=/login">
        </head>
        <body class="bg-gray-100 font-sans min-h-screen flex items-center justify-center">
            <div class="bg-white p-8 rounded-lg shadow-md text-center">
                <h1 class="text-3xl font-bold text-gray-800 mb-4">Bem-vindo ao LearnDo!</h1>
                <p class="text-gray-600 mb-4">Redirecionando para a página de login em 3 segundos...</p>
                <div class="space-x-4">
                    <a href="/login" class="text-blue-500 hover:underline">Login</a>
                    <a href="/register" class="text-blue-500 hover:underline">Cadastre-se</a>
                </div>
            </div>
        </body>
    </html>
    """

@app.get("/home")
def home(request: Request, user=Depends(auth.get_current_user)):
    if not user:
        return templates.TemplateResponse("unauthenticated.html", {"request": request})
    return templates.TemplateResponse("home.html", {"request": request})

app.include_router(auth.router)
app.include_router(alunos.router)
app.include_router(cursos.router)
app.include_router(professores.router)

logger.info("Aplicativo inicializado com sucesso!")