FROM python:3.11-slim AS base
WORKDIR /app
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main
COPY ./src ./src


FROM python:3.11 AS runner
WORKDIR /app
RUN groupadd -r noroot && useradd --no-create-home -r -g noroot noroot
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /app/src ./src

RUN chown -R noroot:noroot /app
USER noroot
ENV PYTHONPATH="/app/src"
EXPOSE 8000
CMD ["uvicorn", "routes_app.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]