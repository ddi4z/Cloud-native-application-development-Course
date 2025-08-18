FROM python:3.11-slim as builder
WORKDIR /app
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-dev
COPY ./src ./src

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.venv /.venv
COPY --from=builder /app/src ./src

ENV PATH="/app/.venv/bin:$PATH"
# Exponer puerto 8000 donde corre el API 
EXPOSE 8000

CMD ["uvicorn", "routes_app.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]