FROM python:3.9.7-buster@sha256:588f672694b3c9caa2be414b4cb2bbd089927f29ac984576acd47ab57b64de12

RUN apt update && apt install -y pipenv
RUN python3 -m pip install --upgrade pip

RUN mkdir $HOME/ludus/
COPY . $HOME/ludus/
WORKDIR $HOME/ludus/

RUN pipenv sync
