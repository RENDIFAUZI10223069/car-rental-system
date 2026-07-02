#!/bin/bash
set -e

echo ">>> [$INSTANCE_NAME] Menunggu PostgreSQL Primary ($POSTGRES_PRIMARY_HOST:$POSTGRES_PRIMARY_PORT) siap..."
until nc -z "$POSTGRES_PRIMARY_HOST" "$POSTGRES_PRIMARY_PORT"; do
    sleep 1
done
echo ">>> [$INSTANCE_NAME] PostgreSQL Primary siap."

echo ">>> [$INSTANCE_NAME] Menunggu Redis ($REDIS_HOST:$REDIS_PORT) siap..."
until nc -z "$REDIS_HOST" "$REDIS_PORT"; do
    sleep 1
done
echo ">>> [$INSTANCE_NAME] Redis siap."

# Hanya backend_1 yang menjalankan migrate & createsuperuser
# agar tidak terjadi race-condition saat 2 instance jalan bersamaan.
if [ "$INSTANCE_NAME" = "backend_1" ]; then
    echo ">>> [$INSTANCE_NAME] Menjalankan migrasi database (ke Primary)..."
    python manage.py migrate --noinput

    echo ">>> [$INSTANCE_NAME] Membuat superuser admin (jika belum ada)..."
    python manage.py bootstrap_admin

    echo ">>> [$INSTANCE_NAME] Mengumpulkan static files..."
    python manage.py collectstatic --noinput
else
    echo ">>> [$INSTANCE_NAME] Menunggu migrasi dari backend_1 selesai..."
    sleep 10
fi

echo ">>> [$INSTANCE_NAME] Menjalankan server Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --log-level info
