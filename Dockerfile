FROM python:3.12.2-alpine3.19 AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /store

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD python manage.py migrate \
    && python manage.py loaddata category.json \
    && python manage.py loaddata items.json \
    && python manage.py runserver 0.0.0.0:8000