FROM tensorflow/tensorflow:2.2.3-gpu-py3

RUN apt-get update
#RUN apt-get install -y build-essential
#RUN apt-get install -y python3-dev python3-pip

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app
ADD main.py /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN python3 --version
EXPOSE 8000

CMD ["gunicorn", "-w 2", "-b", "0.0.0.0:8000", "main:app"]