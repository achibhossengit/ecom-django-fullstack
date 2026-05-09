from django.urls import path
from .views import (
    OrderCreateCustomerView,
    OrderListCustomerView,
    OrderDetailCustomerView,
    OrderCancelCustomerView,
    OrderListManagerView,
    OrderDetailManagerView,
    OrderAssignRiderManagerView,
    OrderCancelManagerView,
)

urlpatterns = [
    # customer
    path('my-dashboard/orders/place/', OrderCreateCustomerView.as_view(), name='customer_order_place'),
    path('my-dashboard/orders/', OrderListCustomerView.as_view(), name='customer_order_list'),
    path('my-dashboard/orders/<int:pk>/', OrderDetailCustomerView.as_view(), name='customer_order_detail'),
    path('my-dashboard/orders/<int:pk>/cancel/', OrderCancelCustomerView.as_view(), name='customer_order_cancel'),
    
    # manager
    path('manager-dashboard/orders/', OrderListManagerView.as_view(), name='manager_order_list'),
    path('manager-dashboard/orders/<int:pk>/', OrderDetailManagerView.as_view(), name='manager_order_detail'),
    path('manager-dashboard/orders/<int:pk>/cancel/', OrderCancelManagerView.as_view(), name='manager_order_cancel'),
    path('manager-dashboard/orders/<int:pk>/assign-rider/', OrderAssignRiderManagerView.as_view(), name='manager_order_assign_rider'),
]