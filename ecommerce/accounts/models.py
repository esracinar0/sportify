from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    class Meta:
        unique_together = ("name", "parent")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("kids", "Kids"),
        ("unisex", "Unisex"),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name="company_products", null=True, blank=True, help_text="Company/Seller who owns this product")
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField(blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)
    material = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['gender', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.brand.name}-{self.name}"
            self.slug = slugify(base)[:300]
        super().save(*args, **kwargs)

    def discounted_price(self):
        if self.discount_percent > 0:
            factor = (Decimal(100) - Decimal(self.discount_percent)) / Decimal(100)
            return (self.price * factor).quantize(Decimal('0.01'))
        return self.price

    def __str__(self):
        return f"{self.brand.name} - {self.name}"

class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("36", "36"), ("37", "37"), ("38", "38"), ("39", "39"),
        ("40", "40"), ("41", "41"), ("42", "42"), ("43", "43"),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    extra_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0.00"))
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "size", "color")

    def price(self):
        return self.product.discounted_price() + self.extra_price

    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True, null=True)
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"Image for {self.product.name}"

    def get_url(self):
        if self.url:
            return self.url
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class Review(models.Model):
    RATING_CHOICES = [(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}" 
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.variant.price() * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"), ("paid", "Paid"), ("shipped", "Shipped"),
        ("delivered", "Delivered"), ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    # Shipping snapshot fields (store address at time of order)
    shipping_full_name = models.CharField(max_length=150, blank=True, default="")
    shipping_phone_number = models.CharField(max_length=40, blank=True, default="")
    shipping_street_address = models.CharField(max_length=255, blank=True, default="")
    shipping_city = models.CharField(max_length=100, blank=True, default="")
    shipping_postal_code = models.CharField(max_length=20, blank=True, default="")
    shipping_country = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

# --- USER PROFILE MODELS ---

class UserProfile(models.Model):
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('company', 'Company/Seller'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=50, default='Türkiye')
    date_of_birth = models.DateField(blank=True, null=True)
    language = models.CharField(max_length=50, default='English')
    promo_emails = models.BooleanField(default=True)
    sms_alerts = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure a UserProfile exists for the user, then save it.
    profile, created = UserProfile.objects.get_or_create(user=instance)
    profile.save()

# --- FIXED ADDRESS MODEL (With Defaults) ---

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_addresses')
    full_name = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=20, default="")
    street_address = models.CharField(max_length=255, default="")
    city = models.CharField(max_length=100, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    postal_code = models.CharField(max_length=20, default="")
    country = models.CharField(max_length=100, default='Türkiye')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

class PaymentMethod(models.Model):
    CARD_TYPES = [('visa', 'Visa'), ('mastercard', 'Mastercard'), ('amex', 'American Express')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    card_holder_name = models.CharField(max_length=100)
    card_number_last4 = models.CharField(max_length=4)
    expiry_date = models.CharField(max_length=5, help_text="MM/YY")
    card_type = models.CharField(max_length=20, choices=CARD_TYPES)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_type.title()} **** {self.card_number_last4}"