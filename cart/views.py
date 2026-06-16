from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from products.models import Product


def get_or_create_cart(request):
    """Get or create cart for user (authenticated or anonymous)"""
    cart = None

    if request.user.is_authenticated:
        # Get or create cart for logged-in user
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If there was a session cart, merge it
        if request.session.session_key:
            session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
            if session_cart and session_cart != cart:
                # Merge session cart items into user cart
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
        # Anonymous user - use session
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

    return cart


def cart_detail(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
        'total_price': cart.total_price,
        'total_items': cart.total_quantity,
    }
    return render(request, 'cart/cart_detail.html', context)


def add_to_cart(request, product_id):
    """Add product to cart (no login required)"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)

    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()
        message = f'Added another {product.name} to your cart'
    else:
        message = f'{product.name} added to your cart'

    # Check if AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': message,
            'cart_count': cart.total_quantity,
        })

    # Regular form submission
    messages.success(request, message)
    next_url = request.GET.get('next', 'cart:cart_detail')
    return redirect(next_url)

def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')

    return redirect('cart:cart_detail')


def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} removed from your cart')
    return redirect('cart:cart_detail')


def clear_cart(request):
    """Clear entire cart"""
    cart = get_or_create_cart(request)
    cart.clear_cart()
    messages.success(request, 'Your cart has been cleared')
    return redirect('cart:cart_detail')


def cart_count(request):
    """Get cart item count (for AJAX)"""
    cart = get_or_create_cart(request)
    count = cart.total_quantity
    return JsonResponse({'count': count})



