from django.urls import path
from .views import home

app_name = 'demo_app'

urlpatterns = [
    path('', home, name='home'),
]
