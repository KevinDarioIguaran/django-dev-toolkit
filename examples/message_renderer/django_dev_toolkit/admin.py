from django.contrib import admin
from .models import (
    Language,

)

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_rtl", "country_code")
    search_fields = ("code", "name")
    list_filter = ("is_rtl",)
    ordering = ("name",)
