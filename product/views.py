import uuid
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .forms import ProductModelForm, CategoryModelForm
from .models import Product, Category, Inventory, PriceHistory, QuantityHistory, CategoryImage, ProductImage


# =====================
# Category Views
# =====================
class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ['core.view_managerdashboard', 'product.view_category']
    queryset = Category.objects.annotate(product_count=Count('products'))
    template_name = "pages/manager_dashboard/category_list.html"
    
class CategoryAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ['core.view_managerdashboard', 'product.add_category']
    form_class = CategoryModelForm
    template_name = "pages/manager_dashboard/category_add.html"
    success_url = reverse_lazy("category_list")
    
    def form_valid(self, form):
        obj = form.save()
        images = self.request.FILES.getlist('images')
        for image in images:
            CategoryImage.objects.create(category=obj, image=image)
        return super().form_valid(form)

class CategoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ['core.view_managerdashboard', 'product.view_category']
    model = Category
    template_name = "pages/manager_dashboard/category_detail.html"

class CategoryEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ['core.view_managerdashboard', 'product.change_category']
    model = Category
    form_class = CategoryModelForm
    template_name = "pages/manager_dashboard/category_edit.html"
    
    def get_success_url(self):
        return reverse_lazy("category_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        obj = form.save()
        deleted_ids = self.request.POST.getlist("delete_images")
        if deleted_ids:
            for img in CategoryImage.objects.filter(id__in=deleted_ids, category=obj):
                img.delete()
        new_images = self.request.FILES.getlist("images")
        for img in new_images:
            CategoryImage.objects.create(category=obj, image=img)
        return super().form_valid(form)

class CategoryRemoveView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ["core.view_managerdashboard", "product.delete_category"]
    queryset = Category.objects.annotate(product_count=Count("products"))
    template_name = "pages/manager_dashboard/category_remove.html"
    success_url = reverse_lazy("category_list")


# ==============================
# Product views
# ==============================
class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ["core.view_managerdashboard", "product.view_product"]
    queryset = Product.objects.select_related('category').select_related('inventory').all()
    template_name = "pages/manager_dashboard/product_list.html"
    
class ProductAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ["core.view_managerdashboard", "product.add_product"]
    form_class = ProductModelForm
    template_name = "pages/manager_dashboard/product_add.html"
    success_url = reverse_lazy("product_list")
    
    def form_valid(self, form):
        price = form.cleaned_data.pop("price")
        quantity = form.cleaned_data.pop("quantity")
        images = self.request.FILES.getlist('images')

        print(f"product images for adding: {images}")
        
        user_id = self.request.user.id
        obj = form.save(commit=False)
        obj.created_by = user_id
        obj.sku = f"{obj.name[:3].upper()}-{uuid.uuid4().hex[:6]}"

        with transaction.atomic():
            obj.save()
            Inventory.objects.create(
                product=obj,
                quantity=quantity,
                price=price
            )
            for image in images:
                ProductImage.objects.create(product=obj, image=image)

        return super().form_valid(form)

class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = ["core.view_managerdashboard", "product.view_product"]
    queryset = Product.objects.select_related('inventory', 'category').all()
    template_name = "pages/manager_dashboard/product_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        try:
            user = User.objects.get(pk=self.object.created_by)
            context["created_by_name"] = user.get_full_name() or user.username
        except User.DoesNotExist:
            context["created_by_name"] = "Unknown"
        return context

class ProductEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ["core.view_managerdashboard", "product.change_product"]
    model = Product
    queryset = Product.objects.select_related('inventory').all()
    form_class = ProductModelForm
    template_name = "pages/manager_dashboard/product_edit.html"

    def get_success_url(self):
        return reverse_lazy("product_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        user_id = self.request.user.id
        product = form.save(commit=False)

        # Current inventory
        inventory = product.inventory
        prev_price = inventory.price
        prev_quantity = inventory.quantity

        # New values from form
        price = form.cleaned_data.pop("price")
        quantity = form.cleaned_data.pop("quantity")

        with transaction.atomic():
            # Update product
            product.created_by = user_id
            product.sku = f"{product.name[:3].upper()}-{uuid.uuid4().hex[:6]}"
            product.save()

            # Update inventory
            inventory.price = price
            inventory.quantity = quantity
            inventory.save()

            # Log histories
            if price != prev_price:
                PriceHistory.objects.create(
                    product=product,
                    last_price=prev_price,
                    price_changed=price - prev_price,
                    created_by = user_id,
                )
            if quantity != prev_quantity:
                QuantityHistory.objects.create(
                    product=product,
                    action_type=QuantityHistory.ActionType.ADJUSTMENT,
                    last_quantity=prev_quantity,
                    quantity_changed=quantity - prev_quantity,
                    created_by = user_id,
                )
                
            # 1. Deleted images
            deleted_ids = self.request.POST.getlist("delete_images")
            if deleted_ids:
                for img in ProductImage.objects.filter(id__in=deleted_ids, product=product):
                    img.delete()  # calls model.delete(), triggers signal

            # 2. New uploaded images
            new_images = self.request.FILES.getlist("images")
            print(f"new images for edit: {new_images}")
            for img in new_images:
                ProductImage.objects.create(product=product, image=img)

        return super().form_valid(form)

class ProductRemoveView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ["core.view_managerdashboard", "product.delete_product"]
    model = Product
    template_name = "pages/manager_dashboard/product_remove.html"
    success_url = reverse_lazy("product_list")
