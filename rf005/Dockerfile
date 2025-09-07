FROM python:3.11 AS builder
LABEL author="j.paterninam@uniandes.edu.co"

WORKDIR /app

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi
COPY src/ /app/src

FROM python:3.11 AS runner
WORKDIR /app

RUN groupadd -r noroot && useradd --no-create-home -r -g noroot noroot
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src
RUN chown -R noroot:noroot /app
USER noroot
EXPOSE 8005

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8005"]
