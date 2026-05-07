from django.db import transaction
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from cart.models import Cart, CartItem
from users.models import UserAddress
from product.models import Inventory, QuantityHistory, Product
from .models import Order, OrderItem, OrderAddress, OrderEvent, OrderStatus


class OrderCreateCustomerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['order.add_order']
    def post(self, request):
        cart_id = request.POST.get('cart_id')
        address_id = request.POST.get('address_id')

        try:
            with transaction.atomic():
                cart = get_object_or_404(Cart, id=cart_id, user_id=request.user.id)
                cart_items = CartItem.objects.filter(cart=cart, selected=True).select_related('product__inventory')

                if not cart_items.exists():
                    messages.error(request, "Your cart is empty.")
                    return redirect('my_cart')

                # validate inventory before doing anything
                for item in cart_items:
                    try:
                        inventory = item.product.inventory
                    except Inventory.DoesNotExist:
                        messages.error(request, f"'{item.product.name}' is no longer available.")
                        return redirect('my_cart')

                    if item.quantity > inventory.quantity:
                        messages.error(request, f"'{item.product.name}' only has {inventory.quantity} units in stock.")
                        return redirect('my_cart')

                subtotal = sum(item.total_price for item in cart_items)
                delivery_charge = 60
                total = subtotal + delivery_charge

                order = Order.objects.create(
                    customer_id=request.user.id,
                    customer_name=request.user.get_full_name() or request.user.username,
                    customer_email=request.user.email,
                    subtotal=subtotal,
                    delivery_charge=delivery_charge,
                    total=total,
                    current_status=OrderStatus.PROCESSSING,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item.product_id,
                        product_name=item.product.name,
                        sku=item.product.sku,
                        price=item.product.inventory.price,
                        quantity=item.quantity,
                    )

                    inventory = item.product.inventory
                    last_quantity = inventory.quantity
                    inventory.quantity -= item.quantity
                    inventory.save()

                    QuantityHistory.objects.create(
                        product=item.product,
                        action_type=QuantityHistory.ActionType.SALE,
                        last_quantity= last_quantity,
                        quantity_changed=-item.quantity,
                        created_by=request.user.id,
                    )

                cart_items.delete()

                user_address = get_object_or_404(
                    UserAddress,
                    id=address_id,
                    user=request.user,
                    is_active=True
                )

                OrderAddress.objects.create(
                    order=order,
                    country_id=user_address.country_id,
                    city_id=user_address.city_id,
                    area_id=user_address.area_id,
                    zone_id=user_address.zone_id,
                    phone_number=user_address.phone_number,
                    name = user_address.name,
                    description=user_address.description,
                    type=user_address.type,
                )

                OrderEvent.objects.create(order=order, status=OrderStatus.PROCESSSING)

        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong while placing your order. Please try again.")
            return redirect('my_cart')

        messages.success(request, "Order placed successfully.")
        return redirect('customer_order_list')

class OrderListCustomerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['order.view_order']
    def get(self, request):
        orders = Order.objects.filter(customer_id=request.user.id).order_by('-created_at')
        return render(request, 'pages/my_dashboard/order_list.html', {'orders': orders})


class OrderDetailCustomerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['order.view_order']
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer_id=request.user.id)
        address = order.address
        items = order.items.all()

        can_cancel = (order.current_status == OrderStatus.PROCESSSING and order.payment_status == Order.PaymentStatus.UNPAID)
        has_pending_payment = (order.payment_status == Order.PaymentStatus.UNPAID and order.current_status != OrderStatus.CANCELLED)

        return render(request, 'pages/my_dashboard/order_detail.html', {
            'order': order,
            'address': address,
            'items': items,
            'can_cancel': can_cancel,
            'has_pending_payment': has_pending_payment,
        })


class OrderCancelCustomerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ['order.cancel_order']
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer_id=request.user.id)

        if order.current_status != OrderStatus.PROCESSSING or order.payment_status != order.PaymentStatus.UNPAID:
            messages.error(request, "This order cannot be cancelled.")
            return redirect('customer_order_detail', pk=pk)

        return render(request, 'pages/my_dashboard/order_cancel_confirm.html', {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer_id=request.user.id)

        if order.current_status != OrderStatus.PROCESSSING or order.payment_status != Order.PaymentStatus.UNPAID:
            messages.error(request, "This order cannot be cancelled.")
            return redirect('customer_order_detail', pk=pk)

        try:
            with transaction.atomic():
                order_items = OrderItem.objects.filter(order=order)

                for item in order_items:
                    product = get_object_or_404(
                        Product.objects.select_related('inventory'),
                        pk=item.product_id
                    )
                    inventory = product.inventory
                    last_quantity = inventory.quantity
                    inventory.quantity += item.quantity
                    inventory.save()

                    QuantityHistory.objects.create(
                        product=product,
                        action_type=QuantityHistory.ActionType.RETURN,
                        last_quantity=last_quantity,
                        quantity_changed=item.quantity,
                        created_by=request.user.id,
                    )

                order.current_status = OrderStatus.CANCELLED
                order.save()
                OrderEvent.objects.create(order=order, status=OrderStatus.CANCELLED)

        except Exception:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('customer_order_detail', pk=pk)

        messages.success(request, "Order cancelled successfully.")
        return redirect('customer_order_detail', pk=pk)
