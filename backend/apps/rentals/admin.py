from django.contrib import admin

from .models import Rental


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = [
        "id", "customer", "car", "driver", "status",
        "tanggal_mulai", "tanggal_rencana_selesai", "tanggal_kembali_aktual", "total_biaya",
    ]
    list_filter = ["status"]
    search_fields = ["customer__nama_lengkap", "car__plat_nomor"]
