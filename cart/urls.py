from django.urls import path
from .views import *

urlpatterns = [
    path('', CartView.as_view(), name="my_cart"),
    path('update/', CartUpdateView.as_view(), name="my_cart_update"),
    path('remove/', CartRemoveView.as_view(), name='my_cart_remove'),
    path('add/', AddToCartView.as_view(), name='my_cart_add'),
]