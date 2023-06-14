ARG BASE_IMAGE=python:3.11.3-slim-buster
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		postgresql-client \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip setuptools wheel

COPY requirements.txt ./
RUN pip3 install --no-cache-dir --verbose -r requirements.txt
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]