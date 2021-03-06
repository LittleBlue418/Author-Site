from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('static_pages.urls')),
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('checkout/', include('checkout.urls')),
    path('fan_art/', include('fan_art.urls')),
    path('products/', include('products.urls')),
    path('profile/', include('profiles.urls')),
    path('shopping_basket/', include('shopping_basket.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
