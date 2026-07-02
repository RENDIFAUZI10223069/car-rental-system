from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.http import JsonResponse

schema_view = get_schema_view(
    openapi.Info(
        title="Car Rental Management API",
        default_version="v1",
        description="Backend Sistem Manajemen Rental Mobil Terdistribusi "
                     "(Docker, Nginx Load Balancer, PostgreSQL Primary-Replica, Redis Cache, JWT)",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/cars/", include("apps.cars.urls")),
    path("api/v1/customers/", include("apps.customers.urls")),
    path("api/v1/drivers/", include("apps.drivers.urls")),
    path("api/v1/rentals/", include("apps.rentals.urls")),

    # Swagger / OpenAPI documentation
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/v1/", api_root, name="api-root"),
]



def api_root(request):
    return JsonResponse({
        "message": "Car Rental System API",
        "version": "v1",
        "endpoints": [
            "/api/v1/auth/",
            "/api/v1/cars/",
            "/api/v1/customers/",
            "/api/v1/drivers/",
            "/api/v1/rentals/",
            "/swagger/",
            "/redoc/",
        ]
    })
