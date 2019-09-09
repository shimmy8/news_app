FROM python:3.7-alpine

COPY . /parser
WORKDIR /parser

RUN apk add --update --update --no-cache \
    g++ \
    gcc \
    libxslt-dev \
    libxml2-dev && \
    pip3 install pipenv && \
    pipenv install
