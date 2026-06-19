from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Display order items inline in order admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'total_price')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin configuration"""
    list_display = ['id', 'full_name', 'email', 'phone', 'total_amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'id']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Customer Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'postal_code')
        }),
        ('Order Details', {
            'fields': ('payment_method', 'status', 'total_amount')
        }),
        ('User Information', {
            'fields': ('user', 'session_key'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']

    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')

    mark_as_processing.short_description = "Mark selected orders as Processing"

    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    mark_as_shipped.short_description = "Mark selected orders as Shipped"

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    mark_as_delivered.short_description = "Mark selected orders as Delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_name', 'quantity', 'product_price', 'total_price']
    list_filter = ['order__status']
    search_fields = ['product_name', 'order__full_name']
    readonly_fields = ['product_name', 'product_price', 'quantity']

    def has_add_permission(self, request):
        return False