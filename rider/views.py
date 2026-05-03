from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect

from .models import RiderApplication
from .forms import RiderApplicationForm


class RiderApplicationListView(LoginRequiredMixin, ListView):
    model = RiderApplication
    template_name = "pages/my_dashboard/rider_application_list.html"
    context_object_name = "applications"

    def get_queryset(self):
        return RiderApplication.objects.filter(
            user=self.request.user
        ).order_by("-applied_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        has_blocking = qs.filter(status__in=["pending", "approved"]).exists()
        context["can_apply"] = (
            self.request.user.has_perm("rider.add_riderapplication")
            and not has_blocking
        )
        return context


class RiderApplicationAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = RiderApplication
    form_class = RiderApplicationForm
    template_name = "pages/my_dashboard/rider_application_form.html"
    permission_required = "rider.add_riderapplication"
    success_url = reverse_lazy("rider_application_list")

    def dispatch(self, request, *args, **kwargs):
        # Block if user already has a pending or approved application
        if request.user.is_authenticated:
            has_blocking = RiderApplication.objects.filter(
                user=request.user,
                status__in=["pending", "approved"]
            ).exists()
            if has_blocking:
                messages.warning(
                    request,
                    "You cannot submit a new application while one is pending or approved."
                )
                return redirect("rider_application_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Your rider application has been submitted successfully!")
        return super().form_valid(form)


class RiderApplicationDetailView(LoginRequiredMixin, DetailView):
    model = RiderApplication
    template_name = "pages/my_dashboard/rider_application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        # Users can only see their own applications
        return RiderApplication.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app = self.object
        user = self.request.user
        is_pending = app.status == "pending"
        is_approved = app.status == "approved"

        context["can_edit"] = (
            user.has_perm("rider.change_riderapplication")
            and app.status == "pending"  # only editable while pending
        )
        context["can_delete"] = (
            user.has_perm("rider.delete_riderapplication")
            and app.status == "pending"
        )

        if is_approved:
            context["lock_message"] = "This application has been approved. You can no longer modify or delete it."
        elif is_pending:
            context["lock_message"] = None  # pending is editable — no lock message needed here
        else:  # rejected
            context["lock_message"] = "This application was rejected and can no longer be modified or deleted."

        return context


class RiderApplicationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = RiderApplication
    form_class = RiderApplicationForm
    template_name = "pages/my_dashboard/rider_application_form.html"
    permission_required = "rider.change_riderapplication"

    def get_queryset(self):
        return RiderApplication.objects.filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        # After super() the object is resolved — guard non-pending
        if hasattr(self, "object") and self.object.status != "pending":
            messages.error(request, "Only pending applications can be edited.")
            return redirect("rider_application_detail", pk=self.object.pk)
        return response

    def get_success_url(self):
        return reverse_lazy("rider_application_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Application updated successfully.")
        return super().form_valid(form)


class RiderApplicationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RiderApplication
    template_name = "pages/my_dashboard/rider_application_confirm_delete.html"
    permission_required = "rider.delete_riderapplication"
    success_url = reverse_lazy("rider_application_list")
    context_object_name = "application"

    def get_queryset(self):
        return RiderApplication.objects.filter(user=self.request.user)

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if hasattr(self, "object") and self.object.status != "pending":
            messages.error(request, "Only pending applications can be deleted.")
            return redirect("rider_application_detail", pk=self.object.pk)
        return response

    def form_valid(self, form):
        messages.success(self.request, "Application removed successfully.")
        return super().form_valid(form)