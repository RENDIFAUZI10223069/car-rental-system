FROM postgres:15-alpine

COPY init-replication.sh /docker-entrypoint-initdb.d/init-replication.sh
RUN chmod +x /docker-entrypoint-initdb.d/init-replication.sh

# Aktifkan wal_level replica agar streaming replication bisa berjalan
CMD ["postgres", \
     "-c", "wal_level=replica", \
     "-c", "max_wal_senders=10", \
     "-c", "max_replication_slots=10", \
     "-c", "hot_standby=on", \
     "-c", "listen_addresses=*"]
