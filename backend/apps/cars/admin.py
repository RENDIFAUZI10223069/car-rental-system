from django.contrib import admin

from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ["plat_nomor", "merk", "model_mobil", "tahun", "status", "harga_sewa_harian"]
    list_filter = ["status", "merk"]
    search_fields = ["plat_nomor", "merk", "model_mobil"]
