from http import HTTPStatus as HTTPstatus  # type: ignore

from fastapi import FastAPI  # type: ignore
from fastapi.responses import HTMLResponse

from learndo.schemas import Message

app = FastAPI()


@app.get("/", response_model=Message, status_code=HTTPstatus.OK)
def read_root():
    return {"message": "Hello World"}


@app.get("/html", response_class=HTMLResponse)
def read_olamundo():
    return "<h1>Hello World</h1>"
