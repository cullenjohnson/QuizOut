# syntax=docker/dockerfile:1

FROM python:3.11-slim

EXPOSE 8000

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-k", "gevent", "-w", "1", "app:app", "-b", "0.0.0.0:8000"]
