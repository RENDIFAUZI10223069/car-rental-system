from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["nama_lengkap", "no_ktp", "no_telepon", "email"]
    search_fields = ["nama_lengkap", "no_ktp", "no_telepon"]
