FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir poetry==1.8.3

# Copiar pyproject y lock, instalar (sin dev)
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

# Copiar source
COPY src /app/src

# Arrancar 
EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "src.routes_app.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]