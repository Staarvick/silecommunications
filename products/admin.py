from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe  # <-- Add this import
from .models import Brand, Category, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category', 'price', 'compare_price',
        'stock', 'stock_status', 'is_featured', 'is_active', 'stock_display'
    ]
    list_filter = ['brand', 'category', 'stock_status', 'is_featured', 'is_active']
    search_fields = ['name', 'sku', 'brand__name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'compare_price', 'stock', 'stock_status', 'is_featured', 'is_active']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'brand', 'category')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price')
        }),
        ('Stock Management', {
            'fields': ('stock', 'low_stock_threshold', 'stock_status'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('main_image', 'additional_images')
        }),
        ('Description', {
            'fields': ('short_description', 'full_description')
        }),
        ('Specifications', {
            'fields': ('specifications',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )

    def stock_display(self, obj):
        if obj.stock <= 0:
            return mark_safe('<span style="color: red;">Out of Stock</span>')
        elif obj.stock <= obj.low_stock_threshold:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock)
        else:
            return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock)

    stock_display.short_description = 'Stock Status'