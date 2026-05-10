from django.urls import path
from .views import home, product_create, product_detail, product_list

app_name = 'demo_app'

urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list, name='product_list'),
    path('products/new/', product_create, name='product_create'),
    path('products/<int:pk>/', product_detail, name='product_detail'),
]
