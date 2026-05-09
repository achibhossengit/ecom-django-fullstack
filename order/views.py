from django.db import transaction
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from cart.models import Cart, CartItem
from users.models import UserAddress
from product.models import Inventory, QuantityHistory, Product
from rider.models import RiderProfile, RiderAddress
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




# =======================
# Manager related views
# =======================
class OrderListManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'order.view_order'

    def get(self, request):
        status_filter = request.GET.get('status', OrderStatus.PROCESSSING)
        payment_filter = request.GET.get('payment_status', '')

        orders = Order.objects.all().order_by('-created_at')

        if status_filter:
            orders = orders.filter(current_status=status_filter)
        if payment_filter:
            orders = orders.filter(payment_status=payment_filter)

        return render(request, 'pages/manager_dashboard/order_list.html', {
            'orders': orders,
            'status_filter': status_filter,
            'payment_filter': payment_filter,
            'status_choices': OrderStatus.choices,
            'payment_choices': Order.PaymentStatus.choices,
        })


class OrderDetailManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'order.view_order'

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.rider_id:
            rider = get_object_or_404(RiderProfile, pk=order.rider_id)
        else:
            rider = None
            
        can_cancel = order.current_status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED] and order.payment_status == order.PaymentStatus.UNPAID
        print(can_cancel)
        can_assign_rider = (
            order.current_status == OrderStatus.PROCESSSING
            and order.payment_status == order.PaymentStatus.PAID
        )
        context = {
            'order': order,
            'rider': rider,
            'can_cancel': can_cancel,
            'can_assign_rider': can_assign_rider,
        }

        return render(request, 'pages/manager_dashboard/order_detail.html', context=context)
        

class OrderCancelManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'order.cancel_order'

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.current_status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            messages.error(request, "This order cannot be cancelled.")
            return redirect('manager_order_detail', pk=pk)

        return render(request, 'pages/manager_dashboard/order_cancel_confirm.html', {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.current_status in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            messages.error(request, "This order cannot be cancelled.")
            return redirect('manager_order_detail', pk=pk)

        try:
            with transaction.atomic():
                order_items = OrderItem.objects.filter(order=order)

                for item in order_items:
                    product = Product.objects.get(pk=item.product_id)
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

        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('manager_order_detail', pk=pk)

        messages.success(request, "Order cancelled successfully.")
        return redirect('manager_order_detail', pk=pk)
    
    
class OrderAssignRiderManagerView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'order.change_order'

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.current_status != OrderStatus.PROCESSSING:
            messages.error(request, "Rider cannot be assigned at this order stage.")
            return redirect('manager_order_detail', pk=pk)

        filter_by = request.GET.get('filter_by', 'area')

        try:
            order_address = order.address
        except OrderAddress.DoesNotExist:
            messages.error(request, "Order has no address.")
            return redirect('manager_order_detail', pk=pk)

        riders = self._get_riders(filter_by, order_address)
        default_rider = riders.first()

        return render(request, 'pages/manager_dashboard/order_assign_rider.html', {
            'order': order,
            'riders': riders,
            'default_rider': default_rider,
            'filter_by': filter_by,
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.current_status not in [OrderStatus.PROCESSSING, OrderStatus.ASSIGNED_RIDER]:
            messages.error(request, "Rider cannot be assigned at this order stage.")
            return redirect('manager_order_detail', pk=pk)

        rider_id = request.POST.get('rider_id')
        if not rider_id:
            messages.error(request, "Please select a rider.")
            return redirect('manager_order_assign_rider', pk=pk)

        rider = get_object_or_404(RiderProfile, pk=rider_id, is_active=True)

        try:
            with transaction.atomic():
                order.rider_id = rider.id
                order.rider_assigned_by = request.user.id
                order.current_status = OrderStatus.ASSIGNED_RIDER
                order.save()
                OrderEvent.objects.create(order=order, status=OrderStatus.ASSIGNED_RIDER)
        except Exception:
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('manager_order_assign_rider', pk=pk)

        messages.success(request, "Rider assigned successfully.")
        return redirect('manager_order_detail', pk=pk)

    def _get_riders(self, filter_by, order_address):
        field_map = {
            'zone':    ('zone_id',    order_address.zone_id),
            'area':    ('area_id',    order_address.area_id),
            'city':    ('city_id',    order_address.city_id),
            'country': ('country_id', order_address.country_id),
        }

        if filter_by in field_map:
            field, value = field_map[filter_by]
            if value:
                return RiderProfile.objects.filter(
                    is_active=True,
                    addresses__is_active=True,
                    **{f'addresses__{field}': value}
                )

        return RiderProfile.objects.filter(is_active=True)