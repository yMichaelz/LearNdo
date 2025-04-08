# LearnDo - Gerenciamento Educacional

## Descrição

O **LearnDo** é uma aplicação web para gerenciamento educacional, permitindo o controle de alunos, professores e cursos. Conta com sistema de autenticação e uma interface responsiva e intuitiva.

## Funcionalidades

- Autenticação de usuários (login e registro)
- CRUD de alunos, professores e cursos
- Página inicial com carrossel e slogan "LearnDo - Gerenciamento Educacional"
- Tratamento de duplicidade com mensagens amigáveis

## Tecnologias

- FastAPI  
- SQLAlchemy  
- PostgreSQL  
- Docker  
- Jinja2  
- Tailwind CSS  

## Pré-requisitos

- Docker e Docker Compose instalados

## Instalação

1. Clonar o repositório:

```bash
git clone https://github.com/yMichaelz/LearNdo && cd learndo
```

2. Criar um arquivo `.env` com o seguinte conteúdo:

```env
DATABASE_URL=postgresql://app_user:app_password@db:5432/learndo_db
```

3. Iniciar a aplicação:

```bash
docker-compose up --build
```

4. Para recriar o banco de dados (se necessário):

```bash
docker-compose down --volumes && docker-compose up --build
```

5. Acessar a aplicação:

```bash
http://localhost:8000
```

## Uso

- Acesse `/register` para criar um novo usuário (exemplo: `admin` / `admin123`)
- Faça login em `/login` e será redirecionado para `/home`
- Gerencie dados nas rotas:
  - `/alunos`
  - `/professores`
  - `/cursos`

## Estrutura do Projeto

```plaintext
projeto/
├── app/
│   ├── main.py
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   ├── templates/
│   └── static/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Personalização

Adicione imagens ao carrossel em `app/static/images/` e atualize `home.html` para refletir as mudanças.

## Resolução de Problemas

- **Imagens não aparecendo**: verifique o caminho correto em `app/static/images/`.
- **Erros gerais**: consulte os logs com `docker-compose logs learndo_app-1`.
- **Banco não conecta**: verifique a variável `DATABASE_URL` no `.env`.

