FROM nvidia/cuda:11.4.1-cudnn8-runtime-ubuntu18.04

RUN apt-get update && \
    apt install -y bash \
                   build-essential \
                   git \
                   curl \
                   python3 \
                   python3-pip

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app
ADD main.py /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-w 2", "-b", "0.0.0.0:8000", "main:app"]