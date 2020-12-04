FROM python:3-slim-buster
RUN apt update && apt upgrade -y && apt install -y bash ffmpeg git && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip && pip3 install pipenv
RUN git clone https://github.com/inAudible-NG/tables.git /rcrack-tables

COPY Pipfile* /tmp/

RUN cd /tmp && pipenv install --deploy --system && mkdir /app

COPY app/ /app

ENV AC_RCRACK "/rcrack-tables"

WORKDIR /app/

ENTRYPOINT ["python3", "main.py"]
