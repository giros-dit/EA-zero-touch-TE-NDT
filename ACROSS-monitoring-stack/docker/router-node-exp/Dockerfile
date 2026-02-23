FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    net-tools \
    iputils-ping \
    lsb-release

RUN wget https://deb.frrouting.org/frr/keys.asc && \
    apt-key add keys.asc && \
    rm keys.asc

RUN release=$(lsb_release -s -c) && \
    echo "deb https://deb.frrouting.org/frr $release frr-stable" >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    frr \
    frr-pythontools

RUN echo "net.ipv6.conf.all.forwarding=1" >> /etc/sysctl.conf && \
    echo "net.ipv6.conf.default.seg6_enabled=1" >> /etc/sysctl.conf &&\
    echo "net.ipv6.conf.all.seg6_enabled=1" >> /etc/sysctl.conf

COPY node_exporter-1.8.2.linux-amd64 /root/node_exporter-1.8.2.linux-amd64  

RUN cd /root/node_exporter-1.8.2.linux-amd64
RUN useradd -m node_exporter
RUN getent group node_exporter || groupadd node_exporter
RUN usermod -a -G node_exporter node_exporter
RUN mv /root/node_exporter-1.8.2.linux-amd64/node_exporter /usr/local/bin/
RUN chown node_exporter:node_exporter /usr/local/bin/node_exporter
RUN bash -c 'echo "[Unit]" > /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "Description=Node Exporter" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "After=network.target" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "[Service]" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "User=node_exporter" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "Group=node_exporter" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "Type=simple" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "ExecStart=/usr/local/bin/node_exporter" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "[Install]" >> /etc/systemd/system/node_exporter.service'
RUN bash -c 'echo "WantedBy=multi-user.target" >> /etc/systemd/system/node_exporter.service'
CMD ["/usr/local/bin/node_exporter"]

#RUN systemctl daemon-reload
#RUN systemctl start node_exporter