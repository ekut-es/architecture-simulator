FROM python:3.10-alpine

ARG UNAME=archsim
ARG UID=1000
ARG GID=1000
ARG SHELL=sh

RUN apk --update add nodejs-lts npm bash

RUN addgroup -g ${GID} ${UNAME}
RUN adduser -D -u ${UID} -G ${UNAME} -s /bin/${SHELL} ${UNAME}

USER $UNAME

WORKDIR /usr/src/app
COPY --chown=${UNAME}:${UNAME} requirements-dev.txt ./
COPY --chown=${UNAME}:${UNAME} package.json ./
COPY --chown=${UNAME}:${UNAME} package-lock.json ./
RUN pip install -r requirements-dev.txt
RUN npm install

EXPOSE 4173
