from rest_framework import serializers

from apps.cars.models import Car
from apps.cars.serializers import CarSerializer
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer
from apps.drivers.models import Driver
from apps.drivers.serializers import DriverSerializer

from .models import Rental


class RentalListSerializer(serializers.ModelSerializer):
    """Digunakan untuk list/retrieve/history — menampilkan data relasi lengkap (read-only)."""
    customer = CustomerSerializer(read_only=True)
    car = CarSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = Rental
        fields = [
            "id", "customer", "car", "driver",
            "tanggal_mulai", "tanggal_rencana_selesai", "tanggal_kembali_aktual",
            "harga_sewa_harian_snapshot", "total_biaya", "denda_keterlambatan",
            "status", "catatan", "created_at", "updated_at",
        ]


class RentalCreateSerializer(serializers.ModelSerializer):
    """Digunakan untuk membuat transaksi rental baru (menerima ID relasi)."""

    class Meta:
        model = Rental
        fields = [
            "id", "customer", "car", "driver",
            "tanggal_mulai", "tanggal_rencana_selesai", "catatan",
        ]

    def validate_car(self, car: Car):
        if car.status != Car.Status.TERSEDIA:
            raise serializers.ValidationError("Mobil ini sedang tidak tersedia untuk disewa.")
        return car

    def validate_driver(self, driver: Driver):
        if driver is not None and driver.status != Driver.Status.TERSEDIA:
            raise serializers.ValidationError("Driver ini sedang tidak tersedia.")
        return driver

    def validate(self, attrs):
        if attrs["tanggal_rencana_selesai"] < attrs["tanggal_mulai"]:
            raise serializers.ValidationError(
                "Tanggal rencana selesai tidak boleh sebelum tanggal mulai."
            )
        return attrs


class RentalReturnSerializer(serializers.Serializer):
    """Digunakan pada endpoint pengembalian mobil."""
    tanggal_kembali_aktual = serializers.DateField(required=False)
    catatan = serializers.CharField(required=False, allow_blank=True)
