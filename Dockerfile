

FROM node:17.6-slim AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY bundles-src ./bundles-src

RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"


FROM python:3.10-slim
WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


COPY --from=frontend-builder /app/bundles ./bundles


RUN SECRET_KEY="dummy_secret_key_for_build" \
    DEBUG=False \
    ALLOWED_HOSTS="*" \
    YANDEX_GEOCODER_KEY="dummy" \
    python manage.py collectstatic --noinput

CMD ["gunicorn", "star_burger.wsgi:application", "--bind", "0.0.0.0:8000"]