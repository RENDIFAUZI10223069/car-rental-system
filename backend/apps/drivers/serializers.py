from rest_framework import serializers

from .models import Driver


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = [
            "id", "nama_lengkap", "no_sim", "no_telepon",
            "alamat", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
