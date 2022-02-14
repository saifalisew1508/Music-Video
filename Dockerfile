FROM debian:latest

RUN apt update && apt upgrade -y
RUN apt install git curl python3-pip ffmpeg -y
RUN python -m pip install -r requirements.txt
RUN /usr/bin/python3 -m pip install --upgrade pip
RUN curl -sL https://deb.nodesource.com/setup_17.x | bash -
RUN apt-get install -y nodejs
COPY . /app
WORKDIR /app
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt
CMD python3 app.py
