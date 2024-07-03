ARG DOCKER_BUILDKIT=1

FROM python:3.11-slim as python-base

EXPOSE 8000

ENV SPEX_CACHE=0
ENV WORK_DIR=/workspaces

ENV WORK_DIR=/workspaces
WORKDIR ${WORK_DIR}
RUN apt-get update && \
    apt-get install -y make && \
    apt-get clean autoclean && \
    apt-get autoremove --yes

RUN pip install --upgrade pip


COPY dist/*.tar.gz ${WORK_DIR}/dist/nvme_spex.tar.gz
RUN pip install hypercorn dist/nvme_spex.tar.gz[spexsrv]

CMD hypercorn --reload --bind 0.0.0.0:8000 spexsrv.application.app:app
