# Imagen slim más ligera
FROM python:3.11-slim
# Creamos y nos movemos a la carpeta trabajo
WORKDIR /app
# Instalamos poetry
RUN pip install poetry==2.1.1
# Copiamos archivos de configuración en la carpeta /app
COPY poetry.lock pyproject.toml README.md ./
# Copiamos el código fuente de su aplicación a la carpeta /app/src
COPY src/ src/
# Deshabilitamos el ambiente virtual de poetry
RUN poetry config virtualenvs.create false
# Instalamos las dependencias de producción (no de desarrollo)
RUN poetry install --only main
# Modificamos variables de ambiente para la ejecución
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
# Ejecutamos la aplicación
CMD ["uvicorn", "entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "9000"]