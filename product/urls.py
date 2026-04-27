from django.urls import path, include
from .views import *

urlpatterns = [
    # ===================
    # Category urls
    # ==================
    path("categories/", CategoryListView.as_view(), name='category_list'),
    path("categories/add/", CategoryAddView.as_view(), name='category_add'),
    path("categories/<int:pk>/detail/", CategoryDetailView.as_view(), name='category_detail'),
    path("categories/<int:pk>/edit", CategoryEditView.as_view(), name='category_edit'),
    path("categories/<int:pk>/remove", CategoryRemoveView.as_view(), name='category_remove'),

    # =================
    # product urls
    # =================
    path("products/", ProductListView.as_view(), name='product_list'),
    path("products/add/", ProductAddView.as_view(), name='product_add'),
    path("products/<int:pk>/detail/", ProductDetailView.as_view(), name='product_detail'),
    path("products/<int:pk>/edit", ProductEditView.as_view(), name='product_edit'),
    path("products/<int:pk>/remove", ProductRemoveView.as_view(), name='product_remove'),
]
