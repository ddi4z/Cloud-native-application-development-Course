FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install poetry
COPY poetry.lock pyproject.toml ./

# Configurar Poetry para crear el entorno virtual dentro del proyecto
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root --only main


COPY ./src ./src

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /.venv

COPY --from=builder /app/src ./src

ENV PATH="/app/.venv/bin:$PATH"


RUN groupadd -r noroot && useradd --no-create-home -r -g noroot noroot
RUN chown -R noroot:noroot /app
USER noroot


EXPOSE 8000

CMD ["uvicorn", "routes_app.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]