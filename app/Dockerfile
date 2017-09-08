FROM resin/raspberrypi3-python:3.6.1-slim

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN apt-get update
RUN apt-get install -y build-essential libffi-dev libnacl-dev python3-dev

RUN apt-get install libav-tools
RUN apt-get install libopus0
RUN pip install --upgrade youtube_dl
RUN apt-get update
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 80

CMD ["app:bot"]
