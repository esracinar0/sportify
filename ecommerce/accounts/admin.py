from django.contrib import admin
from .models import (
    Brand,
    Category,
    Product,
    ProductVariant,
    ProductImage,
    Review,
    Coupon,
    Cart,
    CartItem,
    Order,
    OrderItem,
    UserProfile,
    Address,
    Favorite,
    PaymentMethod # Added this
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    prepopulated_fields = {"slug": ("name",)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("sku", "size", "color", "stock", "extra_price", "is_active")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "is_active", "is_featured", "created_at")
    list_filter = ("brand", "is_active", "is_featured")
    search_fields = ("name", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (ProductVariantInline, ProductImageInline)

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "product", "size", "color", "stock", "is_active")
    list_filter = ("size", "is_active")
    search_fields = ("sku", "product__name")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("product__name", "user__username")

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "active", "valid_from", "valid_to")
    list_filter = ("active",)
    search_fields = ("code",)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    inlines = (CartItemInline,)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "id")
    inlines = (OrderItemInline,)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "variant", "quantity", "price")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "gender", "country")

# --- FIXED ADDRESS ADMIN ---
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    # Changed 'title' to 'full_name' to match your model
    list_display = ("full_name", "user", "city", "is_default")
    search_fields = ("full_name", "city", "street_address")

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "card_type", "card_number_last4", "is_default")

# Admin Customization
admin.site.site_header = "Sportify Admin"
admin.site.site_title = "Sportify Admin"
admin.site.index_title = "Site Administration"