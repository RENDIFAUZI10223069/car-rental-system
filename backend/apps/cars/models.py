from django.db import models


class Car(models.Model):
    class Status(models.TextChoices):
        TERSEDIA = "tersedia", "Tersedia"
        DISEWA = "disewa", "Disewa"
        MAINTENANCE = "maintenance", "Maintenance"

    plat_nomor = models.CharField(max_length=20, unique=True)
    merk = models.CharField(max_length=100)
    model_mobil = models.CharField(max_length=100)
    tahun = models.PositiveIntegerField()
    warna = models.CharField(max_length=50)
    harga_sewa_harian = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TERSEDIA)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.merk} {self.model_mobil} ({self.plat_nomor})"
