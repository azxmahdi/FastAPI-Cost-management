FROM docker.arvancloud.ir/python:3.12-slim

WORKDIR /usr/src/core

COPY requirements.txt .
RUN pip install -i https://mirror-pypi.runflare.com/simple --upgrade pip && pip install -i https://mirror-pypi.runflare.com/simple -r requirements.txt

COPY ./core .
# CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8000"]
