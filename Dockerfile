FROM python:3.8-slim-buster

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY ./*.py /code/

EXPOSE 5000

CMD gunicorn --workers 5 --bind 0.0.0.0:5000 apiserver:app
