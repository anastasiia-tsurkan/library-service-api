FROM  python:3.10.8-slim-buster
LABEL maintainer="shatalova.anastasiia.of@gmail.com"

WORKDIR /app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY . .
