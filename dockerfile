FROM python:3.8-alpine

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
RUN apk add --update --no-cache postgresql-client jpeg-dev tzdata
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r requirements/dev.txt
RUN apk del .tmp-build-deps

COPY . $APP_HOME

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/home/app/django/entrypoint.sh"]
