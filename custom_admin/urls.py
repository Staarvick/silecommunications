from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Product URLs
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),

    # Brand URLs
    path('brands/', views.brand_list, name='brand_list'),
    path('brands/add/', views.brand_add, name='brand_add'),
    path('brands/edit/<int:brand_id>/', views.brand_edit, name='brand_edit'),
    path('brands/delete/<int:brand_id>/', views.brand_delete, name='brand_delete'),

    # Order URLs (add these)
    path('orders/', views.order_list, name='order_list'),
    path('orders/view/<int:order_id>/', views.order_detail, name='order_detail'),

    # User URLs (add these)
    path('users/', views.user_list, name='user_list'),
    path('users/view/<int:user_id>/', views.user_detail, name='user_detail'),
    path('', views.dashboard, name='dashboard'),

    path('users/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),

]