# products/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand
from django.core.paginator import Paginator

from .models import Product, Category, Brand, CarouselImage  # Make sure CarouselImage is imported


def home(request):
    """Home page view"""
    # Get carousel images from database (admin controlled)
    carousel_images = CarouselImage.objects.filter(is_active=True).order_by('order')

    # Get all active products
    all_products = Product.objects.filter(is_active=True)

    # Get products for carousel (featured or random)
    carousel_products = all_products[:5]

    # Categorized products
    phones = all_products.filter(category__name__icontains='phone')[:4]
    laptops = all_products.filter(category__name__icontains='laptop')[:4]
    solar_products = all_products.filter(category__name__icontains='solar')[:4]

    # All active products ordered by newest first
    products = all_products.order_by('-created_at')

    # Featured products - using correct field names
    featured_products = all_products.filter(
        Q(is_featured=True) | Q(compare_price__isnull=False)
    )[:8]

    # If no featured products found, just show newest products
    if not featured_products:
        featured_products = products[:8]

    # Lipa Pole Pole products - FIXED FIELD NAME
    lipa_pole_pole_products = all_products.filter(
        is_lipa_pole_pole=True
    )[:4]

    # Fallback if no eligible products
    if not lipa_pole_pole_products:
        lipa_pole_pole_products = products[:4]

    categories = Category.objects.filter(is_active=True)[:6]

    context = {
        'carousel_products': carousel_products,
        'carousel_images': carousel_images,  # ← ADD THIS LINE
        'phones': phones,
        'laptops': laptops,
        'solar_products': solar_products,
        'featured_products': featured_products,
        'products': products,
        'categories': categories,
        'lipa_pole_pole_products': lipa_pole_pole_products,
    }

    return render(request, 'home.html', context)

def shop(request):
    """Display all products in shop page"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    brands = Brand.objects.all()

    current_category = request.GET.get('category', '')
    current_brand = request.GET.get('brand', '')
    sort_by = request.GET.get('sort', 'newest')

    if current_category:
        products = products.filter(category__slug=current_category)
    if current_brand:
        products = products.filter(brand__slug=current_brand)

    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'brands': brands,
        'current_category': current_category,
        'current_brand': current_brand,
        'sort_by': sort_by,
    }
    return render(request, 'products/shop.html', context)


def category_products(request, category_slug):
    """Display products by category"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'products/category.html', context)


def brand_products(request, brand_slug):
    """Display products by brand"""
    brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
    products = Product.objects.filter(brand=brand, is_active=True)
    context = {
        'brand': brand,
        'products': products,
    }
    return render(request, 'products/brand_products.html', context)


def product_detail(request, category_slug, brand_slug, product_slug):
    """Display single product details"""
    product = get_object_or_404(
        Product,
        slug=product_slug,
        category__slug=category_slug,
        brand__slug=brand_slug,
        is_active=True
    )
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)


def about(request):
    return render(request, 'products/about.html')


def contact(request):
    return render(request, 'products/contact.html')


def product_list(request):
    """Display all products"""
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def test_images(request):
    products = Product.objects.filter(is_active=True)[:10]
    return render(request, 'products/test.html', {'products': products})


def lipa_pole_pole_view(request):
    """Display products available for Lipa Pole Pole"""
    # Only show products marked as eligible - FIXED FIELD NAME
    products_list = Product.objects.filter(
        is_active=True,
        is_lipa_pole_pole=True  # ← CHANGED THIS LINE
    )

    paginator = Paginator(products_list, 12)  # 12 products per page
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
    }
    return render(request, 'products/lipa_pole_pole.html', context)