ARG NODE_VERSION=8.9.1
FROM mhart/alpine-node:$NODE_VERSION

RUN apk add --update --no-cache bash sudo su-exec && \
    rm -rf /var/cache/* /tmp/* /var/log/* ~/.cache

COPY entrypoint /usr/local/sbin/

RUN chown root /usr/local/sbin/entrypoint && \
    chmod 700 /usr/local/sbin/entrypoint

ENV UNAME="mountebank" \
    GNAME="mountebank" \
    UHOME="/home/mountebank" \
    HOST_UID="1000" \
    HOST_GID="1000" \
    SHELL="/bin/bash"

ENV NPM_CONFIG_LOGLEVEL=error \
    NPM_CONFIG_PRODUCTION=true \
    NODE_ENV=production

ARG MOUNTEBANK_VERSION=1.13.0
RUN npm install -g mountebank@$MOUNTEBANK_VERSION

ARG JSONSCHEMAFAKER_VERSION=0.5.0-rc11
RUN npm install -g json-schema-faker@$JSONSCHEMAFAKER_VERSION

RUN npm cache clean --force

WORKDIR "$UHOME"

ENTRYPOINT ["entrypoint", "mb"]
