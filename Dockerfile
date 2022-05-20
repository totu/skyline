#FROM ubuntu:latest
FROM alpine:edge
RUN echo https://dl-cdn.alpinelinux.org/alpine/edge/testing/ >> /etc/apk/repositories 
RUN apk update && apk add openscad py3-pip git
# ENV DEBIAN_FRONTEND=noninteractive
# RUN apt-get update && apt-get install -y openscad python3-pip git && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip && python3 -m pip install solidpython tqdm
COPY skyline.py /
COPY .docker/run_skyline.sh /
RUN chmod +x /run_skyline.sh
ENTRYPOINT ["/run_skyline.sh"]
