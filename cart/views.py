from django.core.cache import cache
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from product.models import Product
from .models import Cart, CartItem
from .utils import get_cart_cache_key, invalidate_cart_cache

CART_CACHE_TIMEOUT = 60 * 5

class CartView(TemplateView):
    template_name = "pages/my_dashboard/my_cart.html"

    def get_context_data(self, **kwargs):
        request = self.request

        cache_key = get_cart_cache_key(request)
        cached_context = cache.get(cache_key)
        if cached_context:
            return cached_context

        # =======================
        # Logged-in user → DB cart
        # =======================
        if request.user.is_authenticated:
            active_address = request.user.addresses.filter(is_active=True).last()
            cart, _ = Cart.objects.get_or_create(user_id=request.user.id)
            cart_items = CartItem.objects.filter(cart=cart).select_related(
                'product', 'product__inventory'
            ).prefetch_related('product__images')

            total_price = sum(item.total_price for item in cart_items if item.selected)

        # ========================
        # Guest user → session cart
        # ========================
        else:
            active_address = None
            cart = None
            cart_data = request.session.get('cart', [])
            cart_items = []
            total_price = 0
            for item in cart_data:
                try:
                    product = Product.objects.get(id=item["product_id"])
                    total = product.inventory.price * item["quantity"]
                    cart_items.append({
                        "product": product,
                        "quantity": item["quantity"],
                        "selected": item["selected"],
                        "total_price": total,
                    })
                    if item["selected"]:
                        total_price += total
                except Product.DoesNotExist:
                    continue

        shipping_charge = 60
        grand_total = total_price + shipping_charge

        context = {
            "cart": cart,
            "cart_items": cart_items,
            "total_price": total_price,
            "shipping_charge": shipping_charge,
            "grand_total": grand_total,
            "active_address": active_address,
        }
        
        # ====set cache====
        cache.set(cache_key, context, timeout=CART_CACHE_TIMEOUT)
        return context




class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        
        if not product_id:
            messages.error(request, "Product id is missing! Refresh and try again!")
            return redirect(request.META.get("HTTP_REFERER", "my_cart"))

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Product not found! Refresh and try again!")
            return redirect(request.META.get("HTTP_REFERER", "my_cart"))

        # ========================
        # Logged-in user → DB cart
        # ========================
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user_id=request.user.id)
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity, "selected": True}
            )
            if not created:
                item.quantity += quantity
                item.save()
        # ========================
        # Guest user → session cart
        # ========================
        else:
            cart = request.session.get("cart", [])
            found = False
            for item in cart:
                if item["product_id"] == product.id:
                    item["quantity"] += quantity
                    found = True
                    break
            if not found:
                cart.append({
                    "product_id": product.id,
                    "quantity": quantity,
                    "selected": True,
                })
            request.session["cart"] = cart
            request.session.modified = True
            
        invalidate_cart_cache(request)
        return redirect("my_cart")


class CartUpdateView(View):
    def post(self, request, *args, **kwargs):
        valid_action_types = ['toggle_selected', 'quantity_inc', 'quantity_dec']
        item_product_id = request.POST.get('item_product_id')
        action_type = request.POST.get('action_type')

        if not action_type or action_type not in valid_action_types:
            messages.error(request, "Choose a valid action type!")
            return redirect('my_cart')

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user_id=request.user.id)
            cart_item = get_object_or_404(CartItem, product_id=item_product_id, cart=cart)

            if action_type == "toggle_selected":
                cart_item.selected = not cart_item.selected
            elif action_type == "quantity_inc":
                cart_item.quantity += 1
            elif action_type == "quantity_dec":
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                else:
                    messages.warning(request, "Quantity cannot go below 1.")

            cart_item.save()

        else:
            cart_data = request.session.get("cart", [])
            for item in cart_data:
                if str(item["product_id"]) == str(item_product_id):
                    if action_type == "toggle_selected":
                        item["selected"] = not item["selected"]
                    elif action_type == "quantity_inc":
                        item["quantity"] += 1
                    elif action_type == "quantity_dec":
                        if item["quantity"] > 1:
                            item["quantity"] -= 1
                        else:
                            messages.warning(request, "Quantity cannot go below 1.")
                    break
            request.session["cart"] = cart_data
            request.session.modified = True

        invalidate_cart_cache(request)
        return redirect('my_cart')


class CartRemoveView(View):
    def post(self, request, *args, **kwargs):
        item_product_id = request.POST.get('item_product_id')

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user_id=request.user.id)
            cart_item = get_object_or_404(CartItem, product_id=item_product_id, cart=cart)
            cart_item.delete()

        else:
            cart_data = request.session.get("cart", [])
            cart_data = [item for item in cart_data if str(item["product_id"]) != str(item_product_id)]
            request.session["cart"] = cart_data
            request.session.modified = True

        invalidate_cart_cache(request)
        return redirect('my_cart')