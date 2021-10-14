FROM ubuntu:20.10

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8 

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
ADD /src/main.py /app
ADD /src/aad /app/aad

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]