from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from orders.models import Order
from django.contrib import messages
from django.utils.text import slugify

# Import your models
from products.models import Product, Brand, Category
from .decorators import custom_admin_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.text import slugify

from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q
from orders.models import Order, OrderItem

# Import your models
from products.models import Product, Brand, Category
from .decorators import custom_admin_required


# Dashboard view - UPDATED WITH CHART DATA
@login_required
@custom_admin_required
def dashboard(request):
    """Admin dashboard home page with statistics and charts"""

    # Get recent categories (limit to 5 for table)
    recent_categories = Category.objects.all().order_by('-created_at')[:5]

    # ========== BASIC STATS ==========
    total_products = Product.objects.count()
    total_brands = Brand.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    # Additional order status counts for pie chart
    processing_orders = Order.objects.filter(status='processing').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()

    # ========== SALES TREND (Last 7 Days) ==========
    today = timezone.now().date()
    sales_labels = []
    sales_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        sales_labels.append(day.strftime('%b %d'))  # Format: "Jun 15"

        # Sum of completed order amounts for this day
        daily_sales = Order.objects.filter(
            created_at__date=day,
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        sales_data.append(float(daily_sales))

    # ========== CATEGORY DISTRIBUTION ==========
    # Count products per category
    category_distribution = []
    for category in Category.objects.filter(is_active=True):
        product_count = Product.objects.filter(category=category, is_active=True).count()
        if product_count > 0:
            category_distribution.append({
                'name': category.name,
                'count': product_count
            })

    # If no categories have products, show sample data for demonstration
    if not category_distribution:
        category_labels = ['Phones', 'Accessories', 'Solar', 'Tablets', 'Laptops']
        category_counts = [25, 12, 8, 6, 4]
    else:
        category_labels = [cat['name'] for cat in category_distribution]
        category_counts = [cat['count'] for cat in category_distribution]

    # ========== TOP 5 PRODUCTS ==========
    top_products = OrderItem.objects.values('product__name', 'product__id').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    top_products_labels = []
    top_products_data = []

    for item in top_products:
        name = item['product__name']
        # Truncate long names
        if len(name) > 20:
            name = name[:17] + '...'
        top_products_labels.append(name)
        top_products_data.append(item['total_sold'] or 0)

    # If no products sold yet, show sample data
    if not top_products_labels:
        top_products_labels = ['iPhone 15', 'Samsung S24', 'Power Bank', 'Solar Panel', 'AirPods']
        top_products_data = [45, 38, 30, 22, 18]

    context = {
        'title': 'Dashboard',
        'recent_categories': recent_categories,
        # Basic stats
        'total_products': total_products,
        'total_brands': total_brands,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        # Chart data
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
    }
    return render(request, 'custom_admin/dashboard.html', context)




# Product Management Views
@login_required
@custom_admin_required
def product_list(request):
    """List all products"""
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/product_list.html', {
        'products': products,
        'title': 'Products List'
    })


@login_required
@custom_admin_required
def product_add(request):
    """Add new product with image"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            brand_id = request.POST.get('brand')
            category_id = request.POST.get('category')
            price = request.POST.get('price')
            stock = request.POST.get('stock', 0)
            short_description = request.POST.get('short_description', '')
            full_description = request.POST.get('full_description', '')

            # Handle image upload
            main_image = request.FILES.get('main_image')

            if not name:
                messages.error(request, 'Product name is required')
                return redirect('custom_admin:product_add')

            slug = slugify(name)

            # Handle duplicate slug
            if Product.objects.filter(slug=slug).exists():
                slug = f"{slug}-{Product.objects.count() + 1}"

            # Create product
            product = Product.objects.create(
                name=name,
                slug=slug,
                brand_id=int(brand_id) if brand_id else None,
                category_id=int(category_id) if category_id else None,
                price=float(price) if price else 0,
                stock=int(stock) if stock else 0,
                short_description=short_description,
                full_description=full_description,
                main_image=main_image,
                is_active=True
            )

            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('custom_admin:product_list')

        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return redirect('custom_admin:product_add')

    brands = Brand.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'custom_admin/product_form.html', {
        'brands': brands,
        'categories': categories,
        'title': 'Add Product'
    })


@login_required
@custom_admin_required
def product_edit(request, product_id):
    """Edit existing product with image"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            brand_id = request.POST.get('brand')
            category_id = request.POST.get('category')
            price = request.POST.get('price')
            stock = request.POST.get('stock', 0)
            short_description = request.POST.get('short_description', '')
            full_description = request.POST.get('full_description', '')

            product.name = name
            product.brand_id = int(brand_id) if brand_id else None
            product.category_id = int(category_id) if category_id else None
            product.price = float(price) if price else 0
            product.stock = int(stock) if stock else 0
            product.short_description = short_description
            product.full_description = full_description

            # Handle image upload - only update if new image provided
            if request.FILES.get('main_image'):
                product.main_image = request.FILES.get('main_image')

            product.save()

            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('custom_admin:product_list')

        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('custom_admin:product_edit', product_id=product_id)

    brands = Brand.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'custom_admin/product_form.html', {
        'product': product,
        'brands': brands,
        'categories': categories,
        'title': 'Edit Product'
    })


@login_required
@custom_admin_required
def product_delete(request, product_id):
    """Delete a product"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('custom_admin:product_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object': product,
        'object_type': 'Product',
        'cancel_url': 'custom_admin:product_list'
    })


# Category Management Views
@login_required
@custom_admin_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/category_list.html', {
        'categories': categories,
        'title': 'Categories List'
    })


@login_required
@custom_admin_required
def category_add(request):
    """Add new category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            category = Category.objects.create(name=name, description=description)
            messages.success(request, f'Category "{category.name}" added successfully!')
        else:
            messages.error(request, 'Category name is required')
        return redirect('custom_admin:category_list')

    return render(request, 'custom_admin/category_form.html', {
        'title': 'Add Category'
    })


@login_required
@custom_admin_required
def category_delete(request, category_id):
    """Delete a category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object': category,
        'object_type': 'Category',
        'cancel_url': 'custom_admin:category_list'
    })


# Brand Management Views
@login_required
@custom_admin_required
def brand_list(request):
    """List all brands"""
    brands = Brand.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/brand_list.html', {
        'brands': brands,
        'title': 'Brands List'
    })


@login_required
@custom_admin_required
def brand_add(request):
    """Add new brand"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            brand = Brand.objects.create(name=name)
            messages.success(request, f'Brand "{brand.name}" added successfully!')
        else:
            messages.error(request, 'Brand name is required')
        return redirect('custom_admin:brand_list')

    return render(request, 'custom_admin/brand_form.html', {
        'title': 'Add Brand'
    })


@login_required
@custom_admin_required
def brand_delete(request, brand_id):
    """Delete a brand"""
    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'POST':
        brand_name = brand.name
        brand.delete()
        messages.success(request, f'Brand "{brand_name}" deleted successfully!')
        return redirect('custom_admin:brand_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object': brand,
        'object_type': 'Brand',
        'cancel_url': 'custom_admin:brand_list'
    })


from orders.models import Order
from accounts.models import User as CustomUser
from django.core.paginator import Paginator


@login_required
@custom_admin_required
def order_list(request):
    orders_list = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders_list, 20)  # Show 20 orders per page
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)

    context = {
        'orders': orders
    }
    return render(request, 'custom_admin/order_list.html', context)


def order_detail(request, order_id):
    """View order details"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'custom_admin/order_detail.html', context)

def user_list(request):
    """List all users"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    users = CustomUser.objects.all().order_by('-date_joined')
    context = {
        'users': users,
    }
    return render(request, 'custom_admin/user_list.html', context)


def user_detail(request, user_id):
    """View user details"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')

    user = get_object_or_404(CustomUser, id=user_id)
    context = {
        'user_detail': user,
    }
    return render(request, 'custom_admin/user_detail.html', context)


@login_required
@custom_admin_required
def category_edit(request, category_id):
    """Edit existing category"""
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
        else:
            messages.error(request, 'Category name is required')
        return redirect('custom_admin:category_list')

    return render(request, 'custom_admin/category_form.html', {
        'title': 'Edit Category',
        'category': category
    })


@login_required
@custom_admin_required
def brand_edit(request, brand_id):
    """Edit existing brand"""
    brand = get_object_or_404(Brand, id=brand_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        # Add other fields as needed

        if name:
            brand.name = name
            brand.description = description
            # Update other fields
            brand.save()
            messages.success(request, f'Brand "{brand.name}" updated successfully!')
        else:
            messages.error(request, 'Brand name is required')
        return redirect('custom_admin:brand_list')

    return render(request, 'custom_admin/brand_form.html', {
        'title': 'Edit Brand',
        'brand': brand
    })


@login_required
@custom_admin_required
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(CustomUser, id=user_id)

    # Prevent deactivating yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot change your own status!')
        return redirect('custom_admin:user_list')

    user.is_active = not user.is_active
    user.save()

    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User "{user.username}" has been {status}.')
    return redirect('custom_admin:user_list')


@login_required
@custom_admin_required
def user_delete(request, user_id):
    """Delete a user"""
    user = get_object_or_404(CustomUser, id=user_id)

    # Prevent deleting yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('custom_admin:user_list')

    # Prevent deleting superusers (optional, for security)
    if user.is_superuser:
        messages.error(request, 'Super admin users cannot be deleted!')
        return redirect('custom_admin:user_list')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully!')
        return redirect('custom_admin:user_list')

    # If GET request, show confirmation page
    return render(request, 'custom_admin/confirm_delete.html', {
        'object': user,
        'object_type': 'User',
        'cancel_url': 'custom_admin:user_list'
    })