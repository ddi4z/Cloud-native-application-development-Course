FROM python:3.11-slim AS base
LABEL author="me.estevez-breton10@uniandes.edu.co"

RUN pip install poetry \
    && poetry self add poetry-plugin-export

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONPATH=/app/src

COPY --from=base /app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use an user without root privileges
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 9000
CMD ["uvicorn", "src.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "9000"]