from http import HTTPStatus as HTTPstatus  # type: ignore

from fastapi import FastAPI  # type: ignore
from fastapi.responses import HTMLResponse



app = FastAPI()


@app.get("/", status_code=HTTPstatus.OK, response_class=HTMLResponse)
def root():
    return {"message": "Hello World"}

@app.post("/alunos/", status_code=HTTPstatus.CREATED,)
def create_aluno(aluno: Aluno):
    return aluno

@ap.get("/alunos/{aluno_id}", status_code=HTTPstatus.OK)
def get_aluno(aluno_id: int):
    return {"aluno_id": aluno_id}

@app.put("/alunos/{aluno_id}", status_code=HTTPstatus.OK)
def update_aluno(aluno_id: int, aluno: Aluno):
    return {"aluno_id": aluno_id, "aluno": aluno}

@app.delete("/alunos/{aluno_id}", status_code=HTTPstatus.NO_CONTENT)
def delete_aluno(aluno_id: int):
    return {"aluno_id": aluno_id}

@app.post("/cursos/", status_code=HTTPstatus.CREATED)
def create_curso(curso: Curso):
    return curso

@app.get("/cursos/{curso_id}", status_code=HTTPstatus.OK)
def get_curso(curso_id: int):
    return {"curso_id": curso_id}