FROM python:3.10-alpine
LABEL maintainer=kungfudiscomonkey@gmail.com

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_DIR /usr/src/app

# Upgrade Pip
RUN pip install --no-cache-dir -U pip

# Finish installing app
WORKDIR ${APP_DIR}
COPY purplebot ${APP_DIR}/purplebot
COPY docker ${APP_DIR}/docker
COPY setup.* ${APP_DIR}/
RUN set -ex ;\
    apk add --no-cache tini ;\
    apk add --no-cache --virtual build-deps build-base ;\
    pip install --no-cache-dir -r ${APP_DIR}/docker/requirements.txt -e . ;\
    apk del build-deps

USER nobody
EXPOSE 8000

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["purplebot-discord"]
