FROM docker.arvancloud.ir/python:3.12-slim

WORKDIR /usr/src/core

COPY requirements.txt .
RUN pip install -i https://mirror-pypi.runflare.com/simple --upgrade pip && pip install -i https://mirror-pypi.runflare.com/simple -r requirements.txt

COPY ./core .

COPY ./dockerfiles/prod/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]