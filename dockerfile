FROM python:3.8-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /home/app

ENV HOME=/home/app
ENV APP_HOME=/home/app/django
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/drf_static
RUN mkdir $APP_HOME/media
RUN mkdir $APP_HOME/coverage
WORKDIR $APP_HOME

RUN pip install --upgrade pip
COPY ./requirements ./requirements

RUN apt-get update && apt-get -y install netcat gcc postgresql tzdata libpq-dev && apt-get clean
RUN pip install -r requirements/dev.txt

COPY . $APP_HOME

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/home/app/django/entrypoint.sh"]
