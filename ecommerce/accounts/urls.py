from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Search
    path('search/', views.search_page, name='search_page'),
    
    # Categories
    path('category/<str:category_slug>/', views.category_page, name='category_page'),
    
    # Profile & Dashboard
    path('profile/', views.profile_dashboard, name='profile'),
    path('settings/', views.settings_menu, name='settings'),
    
    # Individual Edit Pages
    path('settings/details/', views.account_details, name='account_details'),
    path('settings/phone/', views.edit_phone, name='edit_phone'),
    path('settings/birthday/', views.edit_birthday, name='edit_birthday'),
    path('settings/gender/', views.edit_gender, name='edit_gender'),
    path('settings/notifications/', views.notifications_view, name='notifications'),
    path('settings/location/', views.edit_location, name='edit_location'),
    path('settings/language/', views.language_view, name='language'),
    path('settings/privacy/', views.privacy_view, name='privacy'),
    path('settings/payment/', views.payment_methods_view, name='payment_methods'),
    path('settings/payment/add/', views.add_payment_method, name='add_payment_method'),
    path('settings/addresses/', views.addresses_view, name='addresses'),
    path('settings/addresses/add/', views.add_address_view, name='add_address'),
    path('settings/addresses/delete/<int:addr_id>/', views.delete_address, name='delete_address'),

    # Favorites/Wishlist (FIXED: using correct function name)
    path('favorites/', views.favorites_page, name='favorites'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/check/<int:product_id>/', views.is_in_wishlist, name='check_wishlist'),
    
    # Orders
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # Shopping Cart & Checkout
    path('cart/', views.cart_page, name='cart_page'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:variant_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/decrease/<str:variant_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm/', views.checkout_confirm, name='checkout_confirm'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    
    # Company Dashboard
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('company/product/add/', views.company_add_product, name='company_add_product'),
    path('company/product/<int:product_id>/edit/', views.company_edit_product, name='company_edit_product'),
    path('company/product/<int:product_id>/delete/', views.company_delete_product, name='company_delete_product'),

    # Company Image Management
    path('company/product/image/delete/<int:image_id>/', views.company_delete_image, name='company_delete_image'),
    path('company/product/image/set-primary/<int:image_id>/', views.company_set_primary_image,name='company_set_primary_image'),
]