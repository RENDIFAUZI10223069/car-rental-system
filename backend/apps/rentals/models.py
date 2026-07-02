from django.db import models

from apps.cars.models import Car
from apps.customers.models import Customer
from apps.drivers.models import Driver


class Rental(models.Model):
    class Status(models.TextChoices):
        BERJALAN = "berjalan", "Berjalan"
        SELESAI = "selesai", "Selesai"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="rentals")
    car = models.ForeignKey(Car, on_delete=models.PROTECT, related_name="rentals")
    driver = models.ForeignKey(
        Driver, on_delete=models.PROTECT, related_name="rentals", null=True, blank=True
    )

    tanggal_mulai = models.DateField()
    tanggal_rencana_selesai = models.DateField()
    tanggal_kembali_aktual = models.DateField(null=True, blank=True)

    harga_sewa_harian_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    total_biaya = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    denda_keterlambatan = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BERJALAN)
    catatan = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Rental #{self.id} - {self.customer.nama_lengkap} - {self.car.plat_nomor}"
