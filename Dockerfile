FROM debian:bookworm-slim AS builder

RUN set -ex ; \
  export DEBIAN_FRONTEND=non-interactive ; \
  apt-get update && \
  apt-get install -yy \
    pipx \
    python3-dev && \
  pipx install uv

WORKDIR /app

COPY pyproject.toml uv.lock /app/

ENV PATH=/root/.local/bin:$PATH

RUN uv venv && uv sync

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

WORKDIR /app

COPY --from=builder /app/.venv/ /app/.venv/

RUN set -ex ; \
  addgroup --gid 1000 ddmbot && \
  adduser --disabled-login --uid 1000 --gid 1000 ddmbot

COPY --chmod=0644 devday_mailbot.py /app/devday_mailbot.py

USER ddmbot

ENTRYPOINT ["tini", "/app/.venv/bin/python3", "/app/devday_mailbot.py"]
