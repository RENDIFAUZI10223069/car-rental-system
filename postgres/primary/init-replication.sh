#!/bin/bash
set -e

echo ">>> Membuat role replikasi: ${REPLICATION_USER}"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${REPLICATION_USER}') THEN
            CREATE ROLE ${REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${REPLICATION_PASSWORD}';
        END IF;
    END
    \$\$;
EOSQL

echo ">>> Menambahkan izin replikasi & akses jaringan ke pg_hba.conf"
cat >> "$PGDATA/pg_hba.conf" <<-EOF
# Izinkan replica melakukan streaming replication
host    replication     ${REPLICATION_USER}     0.0.0.0/0               md5
# Izinkan backend Django (di docker network) mengakses database
host    all             all                     0.0.0.0/0               md5
EOF

echo ">>> Selesai konfigurasi replikasi pada Primary"
