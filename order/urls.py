from django.urls import path
from .views import (
    OrderCreateCustomerView,
    OrderListCustomerView,
    OrderDetailCustomerView,
    OrderCancelCustomerView,
)

urlpatterns = [
    # customer
    path('my-dashboard/orders/place/', OrderCreateCustomerView.as_view(), name='customer_order_place'),
    path('my-dashboard/orders/', OrderListCustomerView.as_view(), name='customer_order_list'),
    path('my-dashboard/orders/<int:pk>/', OrderDetailCustomerView.as_view(), name='customer_order_detail'),
    path('my-dashboard/orders/<int:pk>/cancel/', OrderCancelCustomerView.as_view(), name='customer_order_cancel'),
]