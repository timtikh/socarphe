FROM ubuntu:latest


RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt
RUN python3 -m pip install vk_api
RUN python3 -m pip install fuzzywuzzy
RUN pip3 install pyTelegramBotAPI==3.6.6

COPY . /

ENTRYPOINT [ "/bin/bash", "app/docker_entrypoint.sh" ] 


