from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ["nama_lengkap", "no_sim", "no_telepon", "status"]
    list_filter = ["status"]
    search_fields = ["nama_lengkap", "no_sim"]
