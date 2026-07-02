#!/bin/bash
set -e

DATA_DIR="/var/lib/postgresql/data"

if [ -z "$(ls -A "$DATA_DIR" 2>/dev/null)" ]; then
    echo ">>> Data directory kosong. Menunggu Primary siap untuk pg_basebackup..."

    until pg_isready -h "$PRIMARY_HOST" -U "$REPLICATION_USER" >/dev/null 2>&1; do
        echo "Menunggu postgres_primary..."
        sleep 2
    done

    echo ">>> Menjalankan pg_basebackup dari Primary ($PRIMARY_HOST)..."
    until pg_basebackup \
        -h "$PRIMARY_HOST" \
        -D "$DATA_DIR" \
        -U "$REPLICATION_USER" \
        -Fp -Xs -P -R -v; do
        echo "pg_basebackup gagal, mencoba lagi dalam 3 detik..."
        sleep 3
    done

    chmod 0700 "$DATA_DIR"
    echo ">>> pg_basebackup selesai. standby.signal & primary_conninfo sudah otomatis dibuat (-R)."
fi

echo ">>> Menjalankan PostgreSQL sebagai Hot Standby (Read Replica)..."
exec docker-entrypoint.sh postgres -c hot_standby=on -c listen_addresses=*
