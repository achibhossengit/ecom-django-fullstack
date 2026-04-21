from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from users.forms import UserUpdateForm

class ProfileView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = UserUpdateForm(instance=self.user)
        return render(request, "users/user_profile.html", {"form": form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=self.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")

        return render(request, "users/user_profile.html", {"form": form})