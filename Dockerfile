FROM python:3.8-slim-bullseye

RUN apt-get update -y && apt-get upgrade -y \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
locales build-essential \
&& localedef -f UTF-8 -i ja_JP ja_JP.UTF-8 \
&& rm -rf /var/lib/apt/lists/* && apt-get clean && apt-get autoclean && apt-get autoremove \
&& pip install --upgrade pip setuptools pipenv \
&& pip install pipenv

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TERM xterm
ENV TZ JST-9

COPY . /var/kakuninsan
WORKDIR /var/kakuninsan
RUN pipenv install --system --deploy
CMD ["uwsgi", "--ini", "/var/kakeibosan/kakeibosan_docker.ini"]
