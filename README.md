Gunicorn

```
gunicorn "app:init_func()" -b 0.0.0.0:8080 -k aiohttp.GunicornWebWorker
```

Docker

```
docker build -t healthcheck .
docker run -d -p 8080:80 --name healthcheck_web_1 healthcheck
```