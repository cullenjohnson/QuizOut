# syntax=docker/dockerfile:1

FROM python:3.11-slim

EXPOSE 8000

RUN apt-get update
RUN apt-get -y install --no-install-recommends sqlite3

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x docker-run.sh

ENTRYPOINT ["./docker-run.sh"]
