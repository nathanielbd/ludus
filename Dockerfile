FROM python:3.9.7

RUN apt update && apt install -y pipenv
RUN python3 -m pip install --upgrade pip

RUN mkdir $HOME/ludus/
COPY . $HOME/ludus/
WORKDIR $HOME/ludus/

RUN pipenv lock; pipenv install