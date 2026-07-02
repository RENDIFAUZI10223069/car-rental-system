from django.db import models


class Driver(models.Model):
    class Status(models.TextChoices):
        TERSEDIA = "tersedia", "Tersedia"
        BERTUGAS = "bertugas", "Bertugas"
        NONAKTIF = "nonaktif", "Nonaktif"

    nama_lengkap = models.CharField(max_length=150)
    no_sim = models.CharField(max_length=32, unique=True)
    no_telepon = models.CharField(max_length=20)
    alamat = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TERSEDIA)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama_lengkap} ({self.no_sim})"
