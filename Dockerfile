FROM alpine:3.7

RUN apk add --no-cache \
        python3 \
        py3-pip \
        libc-dev

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

WORKDIR /public

CMD [ \
    "gunicorn", \
    "--bind", "0.0.0.0:80", \
    "--workers", "8", \
    "--access-logfile", "access.log", \
    "--logger-class", "CustomLogger.CustomLogger", \
    "app:app" \
]