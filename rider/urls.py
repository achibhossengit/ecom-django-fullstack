from django.urls import path
from .views import (
    RiderApplicationListView,
    RiderApplicationAddView,
    RiderApplicationDetailView,
    RiderApplicationUpdateView,
    RiderApplicationDeleteView,
)

urlpatterns = [
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
]