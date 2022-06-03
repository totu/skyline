FROM alpine:edge
RUN echo https://dl-cdn.alpinelinux.org/alpine/edge/testing/ >> /etc/apk/repositories
RUN apk update && apk add openscad py3-pip git
RUN python3 -m pip install --upgrade pip && python3 -m pip install solidpython tqdm
COPY skyline.py /
COPY .docker/run_skyline.sh /
RUN chmod +x /run_skyline.sh
RUN git config --global --add safe.directory /workspace
ENTRYPOINT ["/run_skyline.sh"]
