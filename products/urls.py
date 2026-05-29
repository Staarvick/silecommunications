# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Remove the empty path '' from here since it's handled in main urls.py
    path('', views.home, name='home'),  # ← This should be first
    path('products/', views.product_list, name='product_list'),  # ← This is for /products/
    path('shop/', views.shop, name='shop'),
    path('shop/', views.shop, name='shop'),
    path('category/<slug:category_slug>/', views.category_products, name='category'),
    path('brand/<slug:brand_slug>/', views.brand_products, name='brand_products'),
    path('product/<slug:category_slug>/<slug:brand_slug>/<slug:product_slug>/',
         views.product_detail,
         name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),


]