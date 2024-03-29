FROM ubuntu:20.04

WORKDIR /srv

RUN apt-get update && apt-get install -y gfortran libopenblas-dev liblapack-dev pip python netcat
#RUN apt-get install -y locales && \
#    sed -i -e 's/#ru_RU ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
#    dpkg-reconfigure --frontend=noninteractive locales

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y language-pack-ru
ENV LANGUAGE ru_RU.UTF-8
#ENV LANG ru_RU.UTF-8
#ENV LC_ALL ru_RU.UTF-8
RUN locale-gen ru_RU.UTF-8 && dpkg-reconfigure locales

#RUN apt-get install -y language-pack-ru
#ENV LANG ru_RU
#ENV LC_ALL ru_RU

COPY requirements.txt .
RUN pip install -U pip
RUN pip install -Ur requirements.txt

COPY app app
COPY scripts scripts
COPY alembic alembic
COPY alembic.ini .

RUN ["chmod", "+x", "./scripts/docker-entrypoint.sh"]
RUN ["chmod", "+x", "./scripts//wait-for.sh"]
CMD ["./scripts/docker-entrypoint.sh"]
