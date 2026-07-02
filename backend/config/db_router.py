class PrimaryReplicaRouter:
    """
    Router untuk arsitektur Distributed Database:

    - Semua operasi WRITE (create/update/delete) -> PostgreSQL Primary ('default')
    - Semua operasi READ (select) -> PostgreSQL Replica ('replica')
    - Migration hanya boleh dijalankan di 'default' (Primary).
      Replica menerima skema melalui Streaming Replication (WAL),
      BUKAN melalui Django migration.
    """

    def db_for_read(self, model, **hints):
        return "replica"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
