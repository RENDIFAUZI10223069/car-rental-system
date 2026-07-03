# Backend Sistem Manajemen Rental Mobil Terdistribusi

Backend API-only sistem manajemen rental mobil, dibangun untuk
mendemonstrasikan konsep **Distributed System** & **Distributed Database**:
Reverse Proxy + Load Balancing (Nginx), 2 instance Django (horizontal scaling),
PostgreSQL Primary-Replica (Streaming Replication), Redis Cache, dan JWT Auth.

## Arsitektur

```
                          ┌─────────────┐
         Client ───────►  │    Nginx    │  (Reverse Proxy + Load Balancer)
       (Swagger)          └──────┬──────┘
                                 │  round-robin
                    ┌────────────┴────────────┐
              ┌─────▼─────┐             ┌─────▼─────┐
              │ backend_1 │             │ backend_2 │   (Django + DRF, 2 instance)
              └─────┬─────┘             └─────┬─────┘
                    │                          │
        ┌───────────┼──────────────────────────┤
        │            \                         /
   ┌────▼────┐   ┌────▼─────────┐   ┌─────────▼──────┐
   │  Redis  │   │ PG Primary   │──►│  PG Replica    │
   │ (cache) │   │ (Read/Write) │   │ (Read Only)    │
   └─────────┘   └──────────────┘   └────────────────┘
                    Streaming Replication (WAL)

   pgAdmin -> mengelola & memonitor kedua database (Primary & Replica)
```

**Alur data:**
1. Client → Nginx → salah satu instance Django (load balancing round-robin).
2. Endpoint **GET** (list mobil/driver/pelanggan/riwayat transaksi): cek Redis dulu.
   Jika cache **hit** → langsung dikembalikan dari Redis (`_source: redis-cache`).
   Jika cache **miss** → ambil dari PostgreSQL **Replica**, simpan ke Redis, lalu kembalikan
   (`_source: postgresql-replica`).
3. Endpoint **POST/PUT/PATCH/DELETE**: selalu ditulis ke PostgreSQL **Primary**, lalu cache
   terkait di-invalidate (dihapus) agar data tidak basi.
4. PostgreSQL Primary mereplikasi seluruh perubahan ke Replica secara otomatis melalui
   **Streaming Replication** (WAL), sehingga Replica selalu near-real-time sinkron.

Routing baca/tulis otomatis dilakukan oleh `config/db_router.py`
(`PrimaryReplicaRouter`) — semua kode aplikasi (`viewsets`) tidak perlu tahu database
mana yang dipakai, kecuali pada modul `rentals` yang secara eksplisit menulis ke
Primary (`.using("default")`) saat membuat/mengubah transaksi agar terhindar dari
race-condition akibat replication lag.

## Stack Teknologi

| Komponen          | Teknologi                           |
|-------------------|-------------------------------------|
| Backend Framework | Django 4.2 + Django REST Framework  |
| Autentikasi       | JWT (djangorestframework-simplejwt) |
| Database          | PostgreSQL 15 (Primary + Replica)   |
| Cache             | Redis 7                             |
| Reverse Proxy/LB  | Nginx                               |
| Orkestrasi        | Docker Compose                      |
| Dokumentasi API   | Swagger/OpenAPI (drf-yasg)          |
| DB Admin GUI      | pgAdmin 4                           |

## Struktur Proyek

```
car-rental-system/
├── docker-compose.yml
├── .env.example
├── nginx/
│   └── nginx.conf                 # reverse proxy + load balancer config
├── postgres/
│   ├── primary/                   # Dockerfile + init script replikasi
│   └── replica/                   # Dockerfile + entrypoint pg_basebackup
└── backend/
    ├── config/
    │   ├── settings.py            # multi-database, redis cache, JWT, swagger
    │   ├── db_router.py           # routing Primary (write) / Replica (read)
    │   └── urls.py
    └── apps/
        ├── accounts/              # Login Admin (JWT)
        ├── cars/                  # CRUD Data Mobil
        ├── customers/             # CRUD Data Pelanggan
        ├── drivers/                # CRUD Data Driver
        ├── rentals/                # Transaksi rental, pengembalian, riwayat
        └── common/                 # Mixin caching Redis yang dipakai bersama
```

## Menjalankan Proyek

### 1. Prasyarat
- Docker & Docker Compose terpasang.

### 2. Konfigurasi environment
```bash
cp .env.example .env
# sesuaikan isi .env bila perlu (password, dsb)
```

### 3. Jalankan seluruh service
```bash
docker compose up --build
```

Tunggu hingga semua container `healthy`/`running`. Urutan startup otomatis:
`postgres_primary` → `postgres_replica` (pg_basebackup) → `redis` →
`backend_1` (migrate + createsuperuser) → `backend_2` → `nginx` → `pgadmin`.

### 4. Akses layanan

| Layanan                      | URL                                             |
|------------------------------|-------------------------------------------------|
| API (via Nginx load balancer)| http://localhost:8080/api/v1/                   |
| Swagger UI                   | http://localhost:8080/swagger/                  |
| ReDoc                        | http://localhost:8080/redoc/                    |
| Django Admin                 | http://localhost:8080/admin/                    |
| pgAdmin                      | http://localhost:5050                           |
| PostgreSQL Primary (host)    | localhost:5432                                  |
| PostgreSQL Replica (host)    | localhost:5433                                  |

Akun Admin default (bisa diubah lewat `.env`):
```
username: admin
password: admin12345
```

## Endpoint API

Semua endpoint (kecuali login) membutuhkan header:
```
Authorization: Bearer <access_token>
```

### Autentikasi
| Method | Endpoint                    | Keterangan             |
|--------|-----------------------------|------------------------|
| POST   | `/api/v1/auth/login/`       | Login admin → dapat access & refresh token |
| POST   | `/api/v1/auth/refresh/`     | Refresh access token   |

### Data Mobil
| Method | Endpoint                  | Keterangan         |
|--------|---------------------------|--------------------|
| GET    | `/api/v1/cars/`           | List mobil (cached)|
| POST   | `/api/v1/cars/`           | Tambah mobil       |
| GET    | `/api/v1/cars/{id}/`      | Detail mobil       |
| PUT/PATCH | `/api/v1/cars/{id}/`   | Update mobil       |
| DELETE | `/api/v1/cars/{id}/`      | Hapus mobil        |

### Data Pelanggan
Sama polanya di `/api/v1/customers/`

### Data Driver
Sama polanya di `/api/v1/drivers/`

### Transaksi Rental
| Method | Endpoint                          | Keterangan                          |
|--------|-------------------------------------|---------------------------------------|
| GET    | `/api/v1/rentals/`                 | List transaksi (cached, dari replica) |
| POST   | `/api/v1/rentals/`                 | Buat transaksi rental baru            |
| GET    | `/api/v1/rentals/{id}/`            | Detail transaksi                       |
| POST   | `/api/v1/rentals/{id}/return/`     | Mengembalikan mobil (hitung denda bila telat) |
| GET    | `/api/v1/rentals/history/`         | Riwayat transaksi (read-only, dari replica) |

Contoh body **create rental**:
```json
{
  "customer": 1,
  "car": 2,
  "driver": 1,
  "tanggal_mulai": "2026-07-02",
  "tanggal_rencana_selesai": "2026-07-05",
  "catatan": "Sewa untuk perjalanan dinas"
}
```

Contoh body **return mobil** (opsional):
```json
{
  "tanggal_kembali_aktual": "2026-07-06",
  "catatan": "Mobil kembali dengan kondisi baik"
}
```

## Verifikasi Konsep Distributed System

- **Load Balancing**: setiap response memiliki header `X-Upstream-Instance` (dari Nginx)
  yang menunjukkan `backend_1` atau `backend_2` yang menangani request — refresh berkali-kali
  untuk melihat round-robin bekerja.
- **Cache-Aside dengan Redis**: setiap response list memiliki field `_source`:
  `"redis-cache"` (cache hit) atau `"postgresql-replica"` (cache miss, baca DB).
- **Streaming Replication**: buka pgAdmin, bandingkan data antara koneksi ke Primary
  (port 5432) dan Replica (port 5433) — perubahan pada Primary akan muncul di Replica
  dalam hitungan milidetik. Replica bersifat **read-only**; percobaan `INSERT` langsung
  ke Replica lewat pgAdmin akan ditolak oleh PostgreSQL.

## Menghentikan & Membersihkan

```bash
docker compose down          # stop semua container
docker compose down -v       # stop + hapus volume (reset seluruh data)
```
