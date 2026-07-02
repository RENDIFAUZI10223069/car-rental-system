from rest_framework import serializers

from .models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "id", "plat_nomor", "merk", "model_mobil", "tahun",
            "warna", "harga_sewa_harian", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
