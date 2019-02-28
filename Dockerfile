FROM python:3.7-alpine

EXPOSE 80
WORKDIR /app
CMD python -m aiohttp.web -H 0.0.0.0 -P 80 app:init_func

COPY Pipfile* ./
RUN apk update \
    && apk add --virtual build-deps gcc git musl-dev linux-headers \
    && pip install --no-cache-dir pipenv \
    && pipenv install --system --deploy \
    && apk del build-deps \
    && rm -rf /var/cache/apk/*

COPY . ./
