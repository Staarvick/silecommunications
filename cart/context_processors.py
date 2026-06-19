# cart/context_processors.py

from .models import Cart


def cart_count(request):
    """Add cart count to all templates"""
    count = 0
    if request.user.is_authenticated:
        # Get cart for logged-in user (without is_active filter)
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            # Count items in cart - adjust based on your CartItem model
            count = cart.items.count()  # If you have a related name 'items'
            # OR if you have a different relationship:
            # count = cart.cartitem_set.count()
    else:
        # For non-logged users, get from session
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
                count = cart.items.count()
            except Cart.DoesNotExist:
                pass

    return {'cart_count': count}