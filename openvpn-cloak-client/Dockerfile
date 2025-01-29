FROM ubuntu:20.04

RUN apt update && apt-get install -y \
    curl \
    openresolv \
    openvpn

COPY *.sh /usr/local/bin/

RUN curl -fsSL https://github.com/cbeuw/Cloak/releases/download/v2.7.0/ck-client-linux-386-v2.7.0 > /usr/local/bin/ck-client
RUN chmod +x /usr/local/bin/ck-client

ENTRYPOINT [ "entry.sh" ]
