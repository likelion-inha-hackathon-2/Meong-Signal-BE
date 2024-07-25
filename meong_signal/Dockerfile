FROM --platform=linux/amd64 python:3.11.4

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /usr/src/app/
COPY . /usr/src/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install daphne

COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY docker-entrypoint.sh /usr/src/app/docker-entrypoint.sh
RUN apt-get update && apt-get install -y dos2unix
RUN dos2unix /usr/src/app/docker-entrypoint.sh
RUN chmod +x /usr/src/app/docker-entrypoint.sh

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "meong_signal.asgi:application"]