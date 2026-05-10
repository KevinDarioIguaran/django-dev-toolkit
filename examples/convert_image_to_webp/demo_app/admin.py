from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'created_at']
    readonly_fields = ['photo_webp']
    search_fields = ['name', 'description']
