from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from cart.models import Cart, CartItem
from .models import Order, OrderItem


def get_or_create_cart(request):
    """Helper function to get or create cart"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        if request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart and session_cart != cart:
                for item in session_cart.items.all():
                    cart_item, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={'quantity': item.quantity}
                    )
                    if not created:
                        cart_item.quantity += item.quantity
                        cart_item.save()
                session_cart.delete()
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)

    return cart


def checkout(request):
    """Checkout page - displays the checkout form"""
    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty. Add some items before checking out.')
        return redirect('cart:cart_detail')

    # If user is logged in, pre-fill form with their info
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }

    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total_price': cart.total_price,
        'total_quantity': cart.total_quantity,
    }
    return render(request, 'orders/checkout.html', context)


def place_order(request):
    """Place order - saves to database"""
    if request.method != 'POST':
        return redirect('cart:cart_detail')

    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')

    # Get form data
    full_name = request.POST.get('full_name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    city = request.POST.get('city')
    postal_code = request.POST.get('postal_code', '')
    payment_method = request.POST.get('payment_method')

    # Validate required fields
    if not all([full_name, email, phone, address, city]):
        messages.error(request, 'Please fill in all required fields.')
        return redirect('orders:checkout')

    try:
        with transaction.atomic():  # Use atomic transaction to ensure all or nothing
            # Create the order
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                postal_code=postal_code,
                payment_method=payment_method,
                total_amount=cart.total_price,
                status='pending'
            )

            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity
                )

            # Clear the cart after successful order
            cart.items.all().delete()

            messages.success(request,
                             f'Order #{order.id} placed successfully! Thank you {full_name}. We will contact you at {phone}.')

            # Redirect to order confirmation page
            return redirect('orders:order_confirmation', order_id=order.id)

    except Exception as e:
        messages.error(request, f'An error occurred while placing your order. Please try again.')
        return redirect('orders:checkout')


def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'orders/order_confirmation.html', context)


def order_history(request):
    """Order history page for logged-in users"""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please login to view your order history.')
        return redirect('accounts:login')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)


def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id)

    # Security: Only allow order owner or admin to view
    if request.user.is_authenticated:
        if order.user != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to view this order.')
            return redirect('orders:order_history')

    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'orders/order_detail.html', context)