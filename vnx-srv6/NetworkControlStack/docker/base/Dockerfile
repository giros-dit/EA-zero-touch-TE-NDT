FROM python:3.9-slim

LABEL maintainer="avillaseca01 <a.villasecam@alumnos.upm.es>"
LABEL description="Docker image for NSC base with Python 3.9 and required packages"

WORKDIR /app

# Copiar el scripts

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y openssh-server iputils-ping && \
    apt-get install curl -y && \
    apt-get install telnetd -y && \
    pip install -r requirements.txt 

