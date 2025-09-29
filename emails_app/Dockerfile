FROM python:3.11-slim 
LABEL author="d.diazm@uniandes.edu.co"


WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]
