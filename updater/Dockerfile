FROM python:3.7-alpine

COPY . /updater
WORKDIR /updater

RUN pip3 install pipenv && \
    pipenv install
