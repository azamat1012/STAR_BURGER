# Стадия 1: Сборка фронтенда
FROM node:17.6.0-slim AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY bundles-src ./bundles-src
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

# Стадия 2: Сборка бэкенда
FROM python:3.10-slim
WORKDIR /app

# Установка системных зависимостей и очистка кэша apt в одном слое (требование урока)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости сначала для ускорения пересборки (требование урока)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Копируем собранный фронтенд из первой стадии
COPY --from=frontend-builder /app/bundles ./bundles

# Собираем статику на этапе сборки образа (требование урока)
RUN SECRET_KEY="dummy" DEBUG=False ALLOWED_HOSTS="*" YANDEX_GEOCODER_KEY="dummy" python manage.py collectstatic --noinput

CMD ["gunicorn", "star_burger.wsgi:application", "--bind", "0.0.0.0:8000"]