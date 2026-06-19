# cart/models.py
from django.db import models
from django.conf import settings  # Import settings instead of User
from products.models import Product


class Cart(models.Model):
    """Shopping cart model - one cart per user"""
    # Use settings.AUTH_USER_MODEL instead of User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Cart for {self.user}"
        return f"Cart (Session: {self.session_key})"

    @property
    def total_items(self):
        """Get total number of unique items in cart"""
        return self.items.count()

    @property
    def total_quantity(self):
        """Get total quantity of all items"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Get total price of all items"""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Individual item in a cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']  # Prevent duplicate products in same cart
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        """Get total price for this item"""
        return self.quantity * self.product.price