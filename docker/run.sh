docker run --name flaskapp --restart=always \
    -p 5000:80 \
    -v /path/to/app/:/app \
    -d jazzdd/alpine-flask