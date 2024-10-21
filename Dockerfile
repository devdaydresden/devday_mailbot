FROM debian:bookworm-slim

RUN set -ex ; \
  export DEBIAN_FRONTEND=non-interactive ; \
  apt-get update && \
  apt-get install -yy \
    python3 \
    tini ; \
  apt-get clean ; \
  rm -rf \
    /var/cache/apt/archives \
    /var/lib/apt/lists/* \
    /var/log/apt/* \
    /var/log/dpkg.log

RUN set -ex ; \
  addgroup --gid 1000 ddmbot && \
  adduser --disabled-login --uid 1000 --gid 1000 ddmbot

COPY devday_mailbot.py /devday_mailbot

RUN chmod 0755 devday_mailbot

USER ddmbot

ENTRYPOINT ["tini", "/devday_mailbot"]
