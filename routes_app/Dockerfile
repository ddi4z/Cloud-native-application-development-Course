FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
# --------------------------- #

RUN pip install poetry
COPY poetry.lock pyproject.toml ./

# Configurar Poetry para crear el entorno virtual dentro del proyecto
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --only main

COPY ./src ./src

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /.venv

ENV PATH="/app/.venv/bin:$PATH"
# ------------------------- #

COPY --from=builder /app/src ./src

EXPOSE 8000

# El CMD simple es correcto, el problema no estaba aquí
CMD ["uvicorn", "routes_app.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]