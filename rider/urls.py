from django.urls import path
from .views import (
    RiderApplicationListView,
    RiderApplicationAddView,
    RiderApplicationDetailView,
    RiderApplicationUpdateView,
    RiderApplicationDeleteView,
    RiderApplicationManagerListView,
    RiderApplicationManagerDetailView,
    RiderApplicationManagerUpdateView,
    RiderApplicationManagerDeleteView,
    RiderProfileManagerListView,
    RiderProfileManagerDetailView,
    RiderProfileManagerDeleteView,
    RiderAddressListView,
    RiderAddressAddView,
    RiderAddressEditView,
    RiderAddressRemoveView,
)

urlpatterns = [
    # =========================================
    # rider application customer related urls
    # =========================================
    path(
        "my-dashboard/be-a-rider/",
        RiderApplicationListView.as_view(),
        name="rider_application_list",
    ),
    path(
        "my-dashboard/be-a-rider/add/",
        RiderApplicationAddView.as_view(),
        name="rider_application_add",
    ),
    path(
        "my-dashboard/be-a-rider/<int:pk>/",
        RiderApplicationDetailView.as_view(),
        name="rider_application_detail",
    ),
    path(
        "my-dashboard/be-a-rider/<int:pk>/edit/",
        RiderApplicationUpdateView.as_view(),
        name="rider_application_edit",
    ),
    path(
        "my-dashboard/be-a-rider/<int:pk>/remove/",
        RiderApplicationDeleteView.as_view(),
        name="rider_application_delete",
    ),

    # =====================================
    # rider application manager related urls
    # ======================================
    path(
        "manager-dashboard/rider-applications/",
        RiderApplicationManagerListView.as_view(),
        name="manager_rider_application_list",
    ),
    path(
        "manager-dashboard/rider-applications/<int:pk>/",
        RiderApplicationManagerDetailView.as_view(),
        name="manager_rider_application_detail",
    ),
    path(
        "manager-dashboard/rider-applications/<int:pk>/update/",
        RiderApplicationManagerUpdateView.as_view(),
        name="manager_rider_application_update",
    ),
    path(
        "manager-dashboard/rider-applications/<int:pk>/remove/",
        RiderApplicationManagerDeleteView.as_view(),
        name="manager_rider_application_delete",
    ),
    
    # ===================================
    # rider profile manager related urls
    # ================================= 
    path(
        "manager-dashboard/rider-profiles/",
        RiderProfileManagerListView.as_view(),
        name="manager_rider_profile_list",
    ),
    path(
        "manager-dashboard/rider-profiles/<int:pk>/",
        RiderProfileManagerDetailView.as_view(),
        name="manager_rider_profile_detail",
    ),
    path(
        "manager-dashboard/rider-profiles/<int:pk>/remove/",
        RiderProfileManagerDeleteView.as_view(),
        name="manager_rider_profile_delete",
    ),
    
    # ===========================
    # Rider address related urls
    # ===========================
    path(
        "rider-dashboard/addresses/",
        RiderAddressListView.as_view(),
        name="rider_address_list",
    ),
    path(
        "rider-dashboard/addresses/add/",
        RiderAddressAddView.as_view(),
        name="rider_address_add",
    ),
    path(
        "rider-dashboard/addresses/<int:pk>/edit/",
        RiderAddressEditView.as_view(),
        name="rider_address_edit",
    ),
    path(
        "rider-dashboard/addresses/<int:pk>/remove/",
        RiderAddressRemoveView.as_view(),
        name="rider_address_remove",
    ),
]