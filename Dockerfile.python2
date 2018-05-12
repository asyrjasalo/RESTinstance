# https://hub.docker.com/r/robotframework/rfdocker
FROM robotframework/rfdocker:3.0.4-python2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# remove comments for testing local timezones
#RUN apk add --update --no-cache tzdata && \
#  rm -rf /var/cache/* /tmp/* /var/log/* ~/.cache
#RUN cp /usr/share/zoneinfo/Europe/Helsinki /etc/localtime
#RUN echo "Europe/Helsinki" >  /etc/timezone

ENV PYTHONPATH src/
COPY src/ src/
