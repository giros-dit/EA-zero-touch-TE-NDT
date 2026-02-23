FROM wbitt/network-multitool:latest

LABEL maintainer="avillaseca01 <a.villasecam@alumnos.upm.es>"
LABEL description="Docker image for final system with iperf3 tool for ACROSS"

RUN apk update && \
    apk add --no-cache iperf3 && \
    rm -rf /var/cache/apk/*

EXPOSE 5201