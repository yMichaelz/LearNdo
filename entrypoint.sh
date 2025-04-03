#!/bin/sh

#executa as migrações do banco de dados
poetry run alembic upgrade head

#executa o servidor
poetry run fastapi run learndo/app.py --host 0.0.0.0