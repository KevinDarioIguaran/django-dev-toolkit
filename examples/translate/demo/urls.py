from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('', include('demo_app.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
