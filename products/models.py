from django.db import models
from django.urls import reverse
import uuid
import time


class Brand(models.Model):
    """Brand like Samsung, iPhone, Nokia, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:brand_products', args=[self.slug])


class Category(models.Model):
    """Category like Smartphones, Normal Phones, TV Sets, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_products', args=[self.slug])


class Product(models.Model):
    """Individual product model"""
    # Basic Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Add null=True

    # Relationships
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Stock Management
    stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=5, help_text="Alert when stock falls below this number")
    is_in_stock = models.BooleanField(default=True)

    # Images
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    additional_images = models.JSONField(default=list, blank=True)

    # Specifications
    specifications = models.JSONField(default=dict, blank=True)

    # Description
    short_description = models.CharField(max_length=300, blank=True)
    full_description = models.TextField(blank=True)

    # Features
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Stock Status Options
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-order'),
        ('coming_soon', 'Coming Soon'),
    ]
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS, default='in_stock')

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_in_stock']),
        ]

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def get_discount_percentage(self):
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.category.slug, self.brand.slug, self.slug])

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided (for new products)
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            # Handle duplicate slugs
            original_slug = self.slug
            counter = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1

        # Auto-generate SKU if not provided
        if not self.sku:
            # Generate a unique SKU
            # Format: CATEGORY CODE + TIMESTAMP + RANDOM
            category_code = self.category.name[:3].upper() if self.category else 'PRD'
            timestamp = str(int(__import__('time').time()))[-6:]
            random_part = str(uuid.uuid4())[:4].upper()
            self.sku = f"{category_code}-{timestamp}-{random_part}"

            # Ensure SKU is truly unique (in case of collision)
            while Product.objects.filter(sku=self.sku).exists():
                random_part = str(uuid.uuid4())[:4].upper()
                self.sku = f"{category_code}-{timestamp}-{random_part}"

        # Auto-update in_stock based on stock quantity and status
        if self.stock is not None:
            if self.stock_status == 'in_stock':
                self.is_in_stock = self.stock > 0
            else:
                self.is_in_stock = False
        else:
            self.is_in_stock = False

        super().save(*args, **kwargs)


