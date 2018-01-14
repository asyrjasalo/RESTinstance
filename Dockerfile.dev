# https://hub.docker.com/r/robotframework/rfdocker
FROM robotframework/rfdocker:3.0.2

RUN apk add --update --no-cache tzdata && \
    cp /usr/share/zoneinfo/Europe/Helsinki /etc/localtime && \
    echo "Europe/Helsinki" > /etc/timezone && \
    rm -rf /var/cache/* /tmp/* /var/log/* ~/.cache

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH src/
COPY src/ src/
