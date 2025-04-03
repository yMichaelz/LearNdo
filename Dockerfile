FROM python:3.13-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR app/
COPY . .

RUN pip install poetry
RUN pip install fastapi["standard"]

RUN poetry config installer.max-workers 10

RUN poetry install --no-interaction --no-ansi

EXPOSE 8000
CMD poetry run fastapi run ./src/learndo/app.py