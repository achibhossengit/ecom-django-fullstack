from django.urls import path
from .views import homepage, ajax_load_countries, ajax_load_cities, ajax_load_areas, ajax_load_zones

urlpatterns = [
    path('', homepage, name='homepage'),
    path('ajax/countries/', ajax_load_countries, name='ajax_load_countries'),
    path('ajax/cities/', ajax_load_cities, name='ajax_load_cities'),
    path('ajax/areas/',  ajax_load_areas,  name='ajax_load_areas'),
    path('ajax/zones/',  ajax_load_zones,  name='ajax_load_zones'),
]
