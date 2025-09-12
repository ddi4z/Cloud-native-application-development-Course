FROM python:3.11 AS base
LABEL author="d.diazm@uniandes.edu.co"

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY src/ src/

FROM python:3.11 AS runner

WORKDIR /app

COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app/src/ /app/src/

RUN groupadd -r noroot && useradd -r -g noroot noroot
RUN chown -R noroot:noroot /app

USER noroot

EXPOSE 9000
CMD ["uvicorn", "src.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "9000"]