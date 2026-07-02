from django.db import models


class Customer(models.Model):
    nama_lengkap = models.CharField(max_length=150)
    no_ktp = models.CharField(max_length=32, unique=True)
    alamat = models.TextField()
    no_telepon = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.nama_lengkap} ({self.no_ktp})"
