FROM python:3.7-alpine

COPY . /api
WORKDIR /api

RUN pip3 install pipenv && \
    pipenv install
