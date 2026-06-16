# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Home page - this will handle the root URL
    path('', views.home, name='home'),

    # Shop and product listing
    path('shop/', views.shop, name='shop'),
    path('products/', views.product_list, name='product_list'),

    # Product detail (note: put more specific paths before generic ones)
    path('product/<slug:category_slug>/<slug:brand_slug>/<slug:product_slug>/',
         views.product_detail,
         name='product_detail'),

    # Category and brand filtering
    path('category/<slug:category_slug>/', views.category_products, name='category'),
    path('brand/<slug:brand_slug>/', views.brand_products, name='brand_products'),

    # Static pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('lipa-pole-pole/', views.lipa_pole_pole_view, name='lipa_pole_pole'),
]