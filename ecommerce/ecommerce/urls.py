"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# ecommerce/urls.py

from django.contrib import admin
from django.urls import path, include
from accounts import views as account_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('shoes/<int:pk>/', account_views.product_detail, name='product_detail'),
    path('api/search/', account_views.search_api, name='search_api'),
    path('shoes/', account_views.shoes_view, name='shoes'),
    path('', account_views.home_view, name='home'),
    path('cart/', account_views.cart_page, name='cart'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve non-media repo images during development (dev-only shortcut)
    urlpatterns += static('/dev_media/products/', document_root=str(settings.BASE_DIR / 'ecommerce' / 'products'))