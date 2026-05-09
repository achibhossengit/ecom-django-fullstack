from django.urls import path
from .views import homepage, ShopView, ShopDetailView, CategoryListView, AboutView, ajax_load_countries, ajax_load_cities, ajax_load_areas, ajax_load_zones

urlpatterns = [
    path('', homepage, name='homepage'),
    path('shop/', ShopView.as_view(), name='shop_page'),
    path('shop/<int:pk>/', ShopDetailView.as_view(), name='shop_detail'),
    path('categories/', CategoryListView.as_view(), name='categories_page'),
    path('about-us/', AboutView.as_view(), name='about'),
    path('ajax/countries/', ajax_load_countries, name='ajax_load_countries'),
    path('ajax/cities/', ajax_load_cities, name='ajax_load_cities'),
    path('ajax/areas/',  ajax_load_areas,  name='ajax_load_areas'),
    path('ajax/zones/',  ajax_load_zones,  name='ajax_load_zones'),
]
