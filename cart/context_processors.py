from .models import Cart
from product.models import Inventory

def cart(request):
    item_count = 0
    subtotal = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.prefetch_related(
                'items__product__inventory'
            ).get(user_id=request.user.id)

            for item in cart.items.all():
                item_count +=1
                subtotal += item.total_price

        except Cart.DoesNotExist:
            pass

    else:
        session_cart = request.session.get('cart', [])

        if session_cart:
            product_ids = [item['product_id'] for item in session_cart]

            prices = {
                inv['product_id']: inv['price']
                for inv in Inventory.objects.filter(
                    product_id__in=product_ids
                ).values('product_id', 'price')
            }

            for item in session_cart:
                qty = item['quantity']
                price = prices.get(item['product_id'], 0)
                item_count += 1
                subtotal += price * qty

    return {
        'cart_item_count': item_count,
        'cart_subtotal': subtotal,
    }