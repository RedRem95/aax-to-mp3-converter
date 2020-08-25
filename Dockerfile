FROM python:3-slim-buster
RUN apt update && apt upgrade -y && apt install -y bash redis ffmpeg unzip git make libssl-dev build-essential && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip && pip3 install pipenv gunicorn
RUN mkdir /media/in && mkdir /media/out && mkdir /media/config && mkdir /app

COPY Pipfile* /tmp/

RUN cd /tmp && pipenv install --deploy --system

COPY docker_run.sh /app/run.sh
COPY create_rcrack_docker.sh /app/create_rcrack_docker.sh
RUN chmod a+x /app/run.sh

COPY docker_config.json /media/config/config.json
COPY main.py /app/main.py
COPY app /app/app/
COPY converter/ /app/converter/
COPY misc/ /app/misc/

WORKDIR /app/converter/RainbowCrack/rcrack_tables
RUN bash /app/create_rcrack_docker.sh || echo "rcrack propably not enabled"

ENV FLASK_DEBUG 0
ENV CONVERTER_SESSION_TYPE "redis"
ENV CONVERTER_CONFIG_PATH "/media/config"
ENV BIND_ADDRESS 8000
ENV AC_RCRACK "/app/converter/RainbowCrack"

EXPOSE 8000

WORKDIR /app/

CMD ["bash", "./run.sh"]
