FROM python:3.6.2-stretch

WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN apt-get update
RUN apt-get install -y build-essential software-properties-common vim libffi-dev 

RUN apt-get update
RUN apt-get install ffmpeg -y
RUN apt-get install libopus0
RUN pip install --upgrade youtube_dl
RUN pip install -r requirements.txt

ADD . /app

EXPOSE 80

CMD ["app:bot"]
