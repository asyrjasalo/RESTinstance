# https://hub.docker.com/r/robotframework/rfdocker
FROM robotframework/rfdocker:3.0.2

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH src/
COPY src/ src/
