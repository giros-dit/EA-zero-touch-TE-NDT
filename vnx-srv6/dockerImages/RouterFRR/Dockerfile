FROM ubuntu:22.04

LABEL maintainer="avillaseca01 <a.villasecam@alumnos.upm.es>"
LABEL description="Docker image for FRR routing daemon"

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    net-tools \
    iputils-ping \
    lsb-release \
    traceroute \
    tcpdump \
    iperf3 \
    openssh-server

RUN mkdir -p /run/sshd

RUN wget https://deb.frrouting.org/frr/keys.asc && \
    apt-key add keys.asc && \
    rm keys.asc

RUN release=$(lsb_release -s -c) && \
    echo "deb https://deb.frrouting.org/frr $release frr-stable" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    frr \
    frr-pythontools

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf && \
    echo "net.ipv6.conf.default.seg6_enabled=1" >> /etc/sysctl.conf &&\
    echo "net.ipv6.conf.all.seg6_enabled=1" >> /etc/sysctl.conf

RUN bash -c 'echo "PermitRootLogin yes" >> /etc/ssh/sshd_config'
RUN bash -c 'echo "PermitEmptyPasswords yes" >> /etc/ssh/sshd_config'
#RUN service ssh start
RUN passwd -d root

ENTRYPOINT ["/usr/sbin/sshd", "-D"]



