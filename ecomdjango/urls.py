from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('my-dashboard/', include('users.urls')),
    path('cart/', include('cart.urls')),
    path('manager-dashboard/', include('product.urls')),
    # path('manager-dashboard/', include('order.urls')),
    path('', include('core.urls')),
] +static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ debug_toolbar_urls()
