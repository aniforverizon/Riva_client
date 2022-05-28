# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /riva-clent

COPY requirements.txt requirements.txt
COPY riva_api-1.10.0b0-py3-none-any.whl riva_api-1.10.0b0-py3-none-any.whl

RUN pip3 install -r requirements.txt
RUN pip3 install riva_api-1.10.0b0-py3-none-any.whl 

COPY . .

EXPOSE 8085

CMD gunicorn --bind 0.0.0.0:8081 run:app
