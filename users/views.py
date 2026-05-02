from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from users.forms import UserUpdateForm, UserAddressForm
from .models import UserAddress

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserUpdateForm(instance=request.user)
        return render(request, "pages/my_dashboard/my_profile.html", {"form": form})

    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")

        return render(request, "pages/my_dashboard/my_profile.html", {"form": form})

class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        addresses = UserAddress.objects.filter(user=request.user).order_by('-is_active')
        return render(request, 'pages/my_dashboard/address_list.html', {'addresses': addresses})

    def post(self, request):
        # toggle active address
        address_id = request.POST.get('address_id')
        address = get_object_or_404(UserAddress, id=address_id, user=request.user)
        UserAddress.objects.filter(user=request.user).update(is_active=False)
        address.is_active = True
        address.save()
        return redirect('my_addresses')

class AddressAddView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserAddressForm()
        context = {'form': form}
        return render(request, 'pages/my_dashboard/address_edit.html', context)
 
    def post(self, request):
        form = UserAddressForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('my_addresses')
        return render(request, 'pages/my_dashboard/address_edit.html', context)


class AddressEditView(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk, user=request.user)
        form = UserAddressForm(instance=address)
        return render(request, 'pages/my_dashboard/address_edit.html', {'form': form})

    def post(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk, user=request.user)
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('my_addresses')
        return render(request, 'pages/my_dashboard/address_edit.html', {'form': form})


class AddressRemoveView(LoginRequiredMixin, View):
    def get(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk, user=request.user)
        return render(request, 'pages/my_dashboard/address_remove.html', {'address': address})

    def post(self, request, pk):
        address = get_object_or_404(UserAddress, id=pk, user=request.user)
        address.delete()
        messages.success(request, 'Address removed successfully.')
        return redirect('my_addresses')