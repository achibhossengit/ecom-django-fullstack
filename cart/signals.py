from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem

@receiver(user_logged_in)
def sync_cart(sender, user, request, **kwargs):
    print("=====called the loged in signals======")
    cart_data = request.session.get('cart', [])
    if cart_data:
        cart, _ = Cart.objects.get_or_create(user_id=user.id)
        for item in cart_data:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product_id=item["product_id"],
                defaults={"quantity": item["quantity"], "selected": item["selected"]}
            )
            if not created:
                cart_item.quantity += item["quantity"]
                cart_item.save()
        request.session['cart'] = []  # clear guest cart