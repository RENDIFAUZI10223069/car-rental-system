from django.core.cache import cache


class RedisCachedListMixin:
    """
    Mixin untuk implementasi pola Cache-Aside dengan Redis pada ModelViewSet.

    Alur:
      1. GET list -> cek Redis dulu.
      2. Jika ada (cache HIT) -> langsung kembalikan dari Redis.
      3. Jika tidak ada (cache MISS) -> ambil dari PostgreSQL Replica,
         simpan ke Redis, lalu kembalikan ke client.
      4. Setiap create/update/delete (yang selalu ke Primary) akan
         menghapus (invalidate) cache terkait agar data tetap konsisten.
    """

    cache_key_prefix = "cache"
    cache_ttl = None  # None -> pakai default TIMEOUT di settings.CACHES

    def get_cache_key(self, request):
        query = request.query_params.urlencode()
        return f"{self.cache_key_prefix}:list:{query}"

    def list(self, request, *args, **kwargs):
        cache_key = self.get_cache_key(request)
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            cached_data["_source"] = "redis-cache"
            return self._response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=self.cache_ttl)
        response.data["_source"] = "postgresql-replica"
        return response

    def _response(self, data):
        from rest_framework.response import Response
        return Response(data)

    def invalidate_list_cache(self):
        # Menghapus semua cache list milik resource ini (semua kombinasi query param)
        try:
            cache.delete_pattern(f"{self.cache_key_prefix}:list:*")
        except AttributeError:
            # fallback jika backend cache tidak mendukung delete_pattern
            cache.clear()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self.invalidate_list_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self.invalidate_list_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.invalidate_list_cache()
