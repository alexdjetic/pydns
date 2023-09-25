FROM alpine:latest

RUN mkdir /app
WORKDIR /app
COPY . /app/

RUN apk --no-cache add python3 && \
    pip3 install dnspython

EXPOSE 53/udp

CMD ["python3", "/app/dns_server.py"]
