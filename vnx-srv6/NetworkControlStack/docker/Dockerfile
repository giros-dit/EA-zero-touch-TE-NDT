FROM ghcr.io/giros-dit/vnx-srv6/network-control-stack-base:latest

LABEL maintainer="avillaseca01 <a.villasecam@alumnos.upm.es>"
LABEL description="Docker image for NSC with services pce src and api rest"

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia todos los archivos .py desde el contexto raíz al contenedor
COPY *.py .