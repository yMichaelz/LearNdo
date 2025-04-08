#!/bin/bash
echo "Aguardando o PostgreSQL estar pronto..."
while ! nc -z learndo_db 5432; do
  sleep 1
done
echo "PostgreSQL está pronto! Iniciando o aplicativo..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload