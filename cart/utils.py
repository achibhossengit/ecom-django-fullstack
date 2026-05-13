from django.core.cache import cache

def get_cart_cache_key(request):
    if not request.session.session_key:
        request.session.create()

    return f"cart_{request.session.session_key}"


def invalidate_cart_cache(request):
    cache_key = get_cart_cache_key(request)

    cache.delete(cache_key)