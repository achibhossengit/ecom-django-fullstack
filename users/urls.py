from django.urls import path
from users.views import ProfileView, AddressView, AddressEditView, AddressRemoveView, AddressAddView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name="my_profile"),
    path('addresses/', AddressView.as_view(), name="my_addresses"),
    path('addresses/add', AddressAddView.as_view(), name="my_addresses_add"),
    path('addresses/<int:pk>/edit/', AddressEditView.as_view(), name="my_addresses_edit"),
    path('addresses/<int:pk>/remove/', AddressRemoveView.as_view(), name="my_addresses_remove"),
]