FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc nginx && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn whitenoise
COPY . .
ENV SECRET_KEY=build-only-key
ENV ALLOWED_HOSTS=*
RUN python manage.py collectstatic --noinput || true

RUN printf 'server {\n    listen 8080;\n    location /robots.txt { alias /app/staticfiles/robots.txt; default_type text/plain; }\n    location /sitemap.xml { proxy_pass http://127.0.0.1:8000; proxy_set_header Host $host; }\n    location /static/ { alias /app/staticfiles/; }\n    location /media/ { alias /app/media/; }\n    location /.well-known/ {\n        alias /app/staticfiles/.well-known/;\n        default_type application/json;\n        add_header Content-Type application/json;\n        add_header Access-Control-Allow-Origin *;\n    }\n    location / {\n        proxy_pass http://127.0.0.1:8000;\n        proxy_set_header Host $host;\n        proxy_set_header X-Forwarded-Proto https;\n        proxy_set_header X-Forwarded-Port 443;\n    }\n}\n' > /etc/nginx/conf.d/app.conf

EXPOSE 8080
CMD nginx && gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 Wowdash.wsgi:application
