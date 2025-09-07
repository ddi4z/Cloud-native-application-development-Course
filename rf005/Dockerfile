FROM python:3.11 AS builder

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock README.md ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

COPY src/ /app/src

FROM python:3.11 AS runner

WORKDIR /app

RUN groupadd -r noroot && useradd --no-create-home -r -g noroot noroot
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src

ENV PYTHONPATH="/app/src"
RUN chown -R noroot:noroot /app
USER noroot
EXPOSE 8005
CMD ["uvicorn", "rf005.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8005"]