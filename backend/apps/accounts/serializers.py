from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login khusus Admin. Hanya user dengan is_staff=True yang boleh login.
    Response JWT disertai informasi profil admin.
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_staff:
            from rest_framework import serializers
            raise serializers.ValidationError("Hanya Admin yang diizinkan mengakses sistem ini.")

        data["username"] = self.user.username
        data["email"] = self.user.email
        data["is_staff"] = self.user.is_staff
        return data
