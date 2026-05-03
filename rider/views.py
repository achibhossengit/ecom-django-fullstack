from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth.models import Group

from .models import RiderApplication, RiderProfile
from .forms import RiderApplicationForm, RiderApplicationStatusForm

# ======================================
# Rider Application Customer related views
# ================================
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
    

# =====================
# Rider Application Manager related views
# =====================
class RiderApplicationManagerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RiderApplication
    template_name = "pages/manager_dashboard/rider_application_list.html"
    context_object_name = "applications"
    permission_required = "rider.view_riderapplication"
    paginate_by = 20

    VALID_STATUSES = {"pending", "approved", "rejected"}

    def get_queryset(self):
        status = self.request.GET.get("status", "pending")
        qs = RiderApplication.objects.select_related("user").order_by("-applied_at")
        if status in self.VALID_STATUSES:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = self.request.GET.get("status", "pending")
        context["status_counts"] = {
            "pending":  RiderApplication.objects.filter(status="pending").count(),
            "approved": RiderApplication.objects.filter(status="approved").count(),
            "rejected": RiderApplication.objects.filter(status="rejected").count(),
        }
        return context


class RiderApplicationManagerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = RiderApplication
    template_name = "pages/manager_dashboard/rider_application_detail.html"
    context_object_name = "application"
    permission_required = "rider.view_riderapplication"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["can_change_status"] = user.has_perm("rider.add_riderprofile")
        context["can_delete"] = user.has_perm("rider.delete_riderprofile")
        return context


class RiderApplicationManagerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = RiderApplication
    form_class = RiderApplicationStatusForm
    permission_required = "rider.add_riderprofile"
    http_method_names = ["post"]   # GET not allowed — actions come from detail page buttons

    def form_valid(self, form):
        application = form.save(commit=False)
        new_status = form.cleaned_data["status"]

        if new_status not in ("approved", "rejected"):
            messages.error(self.request, "Invalid status value.")
            return redirect("manager_rider_application_detail", pk=application.pk)

        application.save()

        if new_status == "approved":
            # Create RiderProfile if one doesn't exist yet
            RiderProfile.objects.get_or_create(
                user=application.user,
                defaults={
                    "phone_number": "",          # rider fills this in later
                    "vehicle_type": application.vehicle_type,
                    "is_active": False,
                },
            )
            # Add user to the Rider group
            rider_group, _ = Group.objects.get_or_create(name="rider")
            application.user.groups.add(rider_group)

            messages.success(
                self.request,
                f"Application approved. A rider profile has been created and "
                f"{application.full_name} has been added to the Rider group."
            )
        else:
            messages.info(self.request, f"Application for {application.full_name} has been rejected.")

        return redirect(reverse("manager_rider_application_list") + "?status=" + new_status)

    def form_invalid(self, form):
        messages.error(self.request, "Something went wrong. Please try again.")
        return redirect("manager_rider_application_detail", pk=self.get_object().pk)


class RiderApplicationManagerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RiderApplication
    template_name = "pages/manager_dashboard/rider_application_confirm_delete.html"
    permission_required = "rider.delete_riderprofile"
    context_object_name = "application"
    success_url = reverse_lazy("manager_rider_application_list")

    def form_valid(self, form):
        app = self.get_object()
        messages.success(self.request, f"Application from {app.full_name} has been permanently removed.")
        return super().form_valid(form)

# ===================================
# Rider Profile Manager related views
# ==================================
class RiderProfileManagerListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RiderProfile
    template_name = "pages/manager_dashboard/rider_profile_list.html"
    context_object_name = "profiles"
    permission_required = "rider.view_riderprofile"
    paginate_by = 20

    def get_queryset(self):
        qs = RiderProfile.objects.select_related("user").order_by("-created_at")
        active_filter = self.request.GET.get("active")
        if active_filter == "true":
            qs = qs.filter(is_active=True)
        elif active_filter == "false":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_filter"] = self.request.GET.get("active", "")
        context["counts"] = {
            "all":      RiderProfile.objects.count(),
            "active":   RiderProfile.objects.filter(is_active=True).count(),
            "inactive": RiderProfile.objects.filter(is_active=False).count(),
        }
        return context


class RiderProfileManagerDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = RiderProfile
    template_name = "pages/manager_dashboard/rider_profile_detail.html"
    context_object_name = "profile"
    permission_required = "rider.view_riderprofile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_delete"] = self.request.user.has_perm("rider.delete_riderprofile")
        return context


class RiderProfileManagerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RiderProfile
    template_name = "pages/manager_dashboard/rider_profile_confirm_delete.html"
    permission_required = "rider.delete_riderprofile"
    context_object_name = "profile"
    success_url = reverse_lazy("manager_rider_profile_list")

    def form_valid(self, form):
        profile = self.get_object()
        # Remove user from Rider group on profile deletion
        rider_group = Group.objects.filter(name="Rider").first()
        if rider_group:
            profile.user.groups.remove(rider_group)
        messages.success(
            self.request,
            f"Rider profile for {profile.user.username} has been permanently removed."
        )
        return super().form_valid(form)