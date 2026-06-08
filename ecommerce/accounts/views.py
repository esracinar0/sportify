from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .models import Product, UserProfile, Favorite, Order, Address, PaymentMethod, CartItem, Brand, ProductVariant, OrderItem, Category, ProductImage
from .forms import LoginForm, RegisterForm, UserUpdateForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm
import uuid

# --- GENERAL VIEWS ---

def home_view(request):
    """Renders the homepage."""
    return render(request, 'home.html')

def shoes_view(request):
    """Renders the list of all active shoes with optional brand filter."""
    shoes = Product.objects.filter(is_active=True)
    
    # Brand filter (supports multiple brands: ?brand=1&brand=2)
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        shoes = shoes.filter(brand__id__in=selected_brands)
    
    # Get all brands for filter
    brands = Brand.objects.all().order_by('name')
    
    shoes_info = [{'shoe': shoe, 'image_url': shoe.images.first().get_url() if shoe.images.first() else None} for shoe in shoes]
    
    return render(request, 'shoes.html', {
        'shoes_info': shoes_info,
        'brands': brands,
        'selected_brands': selected_brands,
    })


# views.py içerisindeki mevcut category_page ve search_page fonksiyonlarını bunlarla değiştirin:

def category_page(request, category_slug):
    """Renders products filtered by gender, category, brand, size and sorting."""
    # 1. Cinsiyet Kategorisi Eşleştirme
    gender_map = {
        'men': 'men',
        'women': 'women',
        'kids': 'kids',
        'sport': 'men',
    }
    gender = gender_map.get(category_slug)
    if not gender:
        return redirect('shoes') # 'shoes_view' yerine 'shoes' (url name'ine göre)
    
    # 2. Ürünleri Başlangıçta Filtrele
    products = Product.objects.filter(is_active=True, gender=gender)
    
    # 3. Requestten Gelen Filtre Parametrelerini Al
    selected_category_slug = request.GET.get('category') # URL'den gelen ek kategori filtresi
    selected_brands = request.GET.getlist('brand')
    selected_sizes = request.GET.getlist('size')
    sort_by = request.GET.get('sort', 'newest')
    
    # 4. Kategori Filtresi (Örn: Running veya Sneakers gibi alt kategoriler)
    if selected_category_slug:
        products = products.filter(category__slug=selected_category_slug)
    
    # 5. Marka Filtresi
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)
        
    # 6. Beden ve Stok Filtresi
    if selected_sizes:
        products = products.filter(
            variants__size__in=selected_sizes,
            variants__stock__gt=0,
            variants__is_active=True
        ).distinct()
        
    # 7. Sıralama
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # 8. Sayfalama
    from django.core.paginator import Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)
    try:
        products_page = paginator.page(page)
    except:
        products_page = paginator.page(1)
    
    # 9. Filtreler için Gerekli Veriler
    brands = Brand.objects.all().order_by('name')
    categories = Category.objects.all() # Yeni eklenen: Tüm alt kategorileri getir
    all_sizes = ["36", "37", "38", "39", "40", "41", "42", "43"]
    
    shoes_info = [
        {'shoe': p, 'image_url': p.images.first().get_url() if p.images.first() else None}
        for p in products_page
    ]
    
    return render(request, 'category.html', {
        'category': category_slug, # URL'deki ana cinsiyet
        'category_filter': selected_category_slug, # Filtrede seçili olan alt kategori
        'category_title': category_slug.title(),
        'shoes_info': shoes_info,
        'brands': brands,
        'categories': categories, # Template'e gönderildi
        'all_sizes': all_sizes,
        'selected_brands': selected_brands,
        'selected_sizes': selected_sizes,
        'sort_by': sort_by,
        'page_obj': products_page,
        'total_results': paginator.count,
    })


def search_page(request):
    """Dedicated search results page with advanced filtering."""
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    selected_brands = request.GET.getlist('brand')
    selected_sizes = request.GET.getlist('size')
    sort_by = request.GET.get('sort', 'newest')
    
    products = Product.objects.filter(is_active=True)
    
    # Arama
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query) | Q(description__icontains=query)
        )
    
    # Kategori Filtresi
    if category_filter:
        products = products.filter(category__slug=category_filter)
        
    # Marka Filtresi
    if selected_brands:
        products = products.filter(brand__id__in=selected_brands)
        
    # Beden ve Stok Filtresi
    if selected_sizes:
        products = products.filter(
            variants__size__in=selected_sizes,
            variants__stock__gt=0,
            variants__is_active=True
        ).distinct()
    
    # Sıralama
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    else:  # newest
        products = products.order_by('-created_at')
    
    # Sayfalama
    from django.core.paginator import Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)
    try:
        products_page = paginator.page(page)
    except:
        products_page = paginator.page(1)
    
    categories = Category.objects.all()
    brands = Brand.objects.all().order_by('name')
    all_sizes = ["36", "37", "38", "39", "40", "41", "42", "43"]
    
    shoes_info = [
        {'shoe': p, 'image_url': p.images.first().get_url() if p.images.first() else None}
        for p in products_page
    ]
    
    context = {
        'query': query,
        'shoes_info': shoes_info,
        'categories': categories,
        'brands': brands,
        'all_sizes': all_sizes,
        'category_filter': category_filter,
        'selected_brands': selected_brands,
        'selected_sizes': selected_sizes,
        'sort_by': sort_by,
        'page_obj': products_page,
        'total_results': paginator.count,
    }
    
    return render(request, 'search.html', context)

def product_detail(request, pk):
    """Renders the details of a single product."""
    product = get_object_or_404(Product, pk=pk)
    image_url = product.images.first().get_url() if product.images.first() else None
    variants_info = [{'variant': v, 'price': v.price()} for v in product.variants.filter(is_active=True)]
    
    context = {
        'product': product,
        'image_url': image_url,
        'discounted_price_value': product.discounted_price(),
        'variants_info': variants_info,
    }
    return render(request, 'product_detail.html', context)


def search_api(request):
    """Simple JSON search API for products. Returns up to 10 matches."""
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(description__icontains=q)
        ).filter(is_active=True)[:10]

        for p in products:
            image = p.images.first()
            results.append({
                'id': p.id,
                'name': p.name,
                'brand': p.brand.name if p.brand else '',
                'price': str(p.price),
                'image_url': image.get_url() if image else None,
                'description': (p.description or '')[:200],
            })

    return JsonResponse({'results': results})


# --- AUTHENTICATION VIEWS ---

def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    """Handles user registration."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    """Handles user logout."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# --- DASHBOARD & SETTINGS MENU ---

@login_required
def profile_dashboard(request):
    """Renders the main Profile dashboard."""
    return render(request, 'profile_dashboard.html')

@login_required
def settings_menu(request):
    """Renders the Settings menu (list of icons)."""
    UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'settings.html')

# --- INDIVIDUAL SETTINGS VIEWS ---

@login_required
def account_details(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Account details updated!')
            return redirect('profile') 
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    return render(request, 'account_details.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def edit_phone(request):
    if request.method == 'POST':
        request.user.profile.phone_number = request.POST.get('phone')
        request.user.profile.save()
        messages.success(request, 'Phone number updated!')
        return redirect('profile')
    return render(request, 'edit_field.html', {'label': 'Phone Number', 'field_name': 'phone', 'value': request.user.profile.phone_number})

@login_required
def edit_birthday(request):
    if request.method == 'POST':
        request.user.profile.date_of_birth = request.POST.get('birthday')
        request.user.profile.save()
        messages.success(request, 'Birthday updated!')
        return redirect('profile')
    current_dob = request.user.profile.date_of_birth.strftime('%Y-%m-%d') if request.user.profile.date_of_birth else ""
    return render(request, 'edit_field.html', {'label': 'Birthday', 'field_name': 'birthday', 'type': 'date', 'value': current_dob})

@login_required
def edit_gender(request):
    if request.method == 'POST':
        request.user.profile.gender = request.POST.get('gender')
        request.user.profile.save()
        messages.success(request, 'Gender updated!')
        return redirect('profile')
    return render(request, 'edit_gender.html')

@login_required
def edit_location(request):
    if request.method == 'POST':
        request.user.profile.country = request.POST.get('location')
        request.user.profile.save()
        messages.success(request, 'Location updated!')
        return redirect('profile')
    return render(request, 'edit_location.html')

@login_required
def notifications_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.promo_emails = 'promo_emails' in request.POST
        profile.sms_alerts = 'sms_alerts' in request.POST
        profile.save()
        messages.success(request, 'Notification preferences saved.')
        return redirect('profile')
    return render(request, 'notifications.html')

@login_required
def language_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.language = request.POST.get('language', 'English')
        profile.save()
        messages.success(request, 'Language preference updated.')
        return redirect('profile')
    return render(request, 'language.html')

@login_required
def privacy_view(request):
    return render(request, 'privacy.html')

# --- PAYMENT METHODS ---

@login_required
def payment_methods_view(request):
    methods = PaymentMethod.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    cart = request.session.get('cart', {})
    cart_has_items = bool(cart)
    return render(request, 'payment_methods.html', {'methods': methods, 'cart_has_items': cart_has_items})

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        card_num = request.POST.get('card_number') or ""
        # Keep only digits when extracting last 4 (handles spaces/dashes)
        digits = ''.join(ch for ch in card_num if ch.isdigit())
        last4 = digits[-4:] if digits else (card_num.replace(' ', '')[-4:] if card_num else "0000")
        PaymentMethod.objects.create(
            user=request.user,
            card_holder_name=request.POST.get('card_holder'),
            card_number_last4=last4,
            expiry_date=request.POST.get('expiry'),
            card_type='visa'
        )
        messages.success(request, 'Payment method added successfully!')
        return redirect('payment_methods')
    return render(request, 'add_payment_method.html')

# --- ADDRESSES ---

@login_required
def addresses_view(request):
    """List all saved addresses."""
    # Note: Using .filter() is safer than assuming a related_name is set
    addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
    return render(request, 'addresses.html', {'addresses': addresses})

@login_required
def add_address_view(request):
    """Form to add a new delivery address."""
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone'),
            street_address=request.POST.get('address'),
            city=request.POST.get('city'),
            postal_code=request.POST.get('zip'),
            country=request.POST.get('country')
        )
        messages.success(request, 'Address saved successfully!')
        # If we are in a checkout flow (payment method stored), continue to address selection
        if request.session.get('checkout_pm_id'):
            return redirect('checkout_address')
        # Otherwise go to addresses list
        return redirect('addresses')
    return render(request, 'add_address.html')


@login_required
def delete_address(request, addr_id):
    if request.method != 'POST':
        return redirect('addresses')

    try:
        addr = Address.objects.get(id=addr_id, user=request.user)
    except Address.DoesNotExist:
        messages.error(request, 'Address not found.')
        return redirect('addresses')

    addr.delete()
    messages.success(request, 'Address deleted.')
    # If in checkout flow, return to address selection
    if request.session.get('checkout_pm_id'):
        return redirect('checkout_address')
    return redirect('addresses')

# --- USER PROFILE SECTIONS - FAVORITES/WISHLIST ---

@login_required
def favorites_page(request):
    """Display user's favorite products - FIXED VERSION"""
    # Kullanıcının favorilerini al
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'product', 'product__brand', 'product__category'
    )
    
    # Her ürün için resim bilgisi hazırla
    favorites_info = []
    for fav in favorites:
        image_url = None
        if fav.product.images.first():
            image_url = fav.product.images.first().get_url()
        
        favorites_info.append({
            'product': fav.product,
            'image_url': image_url,
            'favorite_id': fav.id
        })
    
    context = {
        'favorites': favorites,
        'favorites_info': favorites_info,
    }
    
    return render(request, 'favorites.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """AJAX endpoint to add product to wishlist - FIXED"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} added to wishlist',
            'is_favorited': True
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def remove_from_wishlist(request, product_id):
    """AJAX endpoint to remove product from wishlist - FIXED"""
    if request.method == 'POST':
        try:
            fav = Favorite.objects.get(user=request.user, product_id=product_id)
            product_name = fav.product.name
            fav.delete()
            return JsonResponse({
                'status': 'success',
                'message': f'{product_name} removed from wishlist',
                'is_favorited': False
            })
        except Favorite.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not in wishlist'}, status=404)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def is_in_wishlist(request, product_id):
    """AJAX endpoint to check if product is in wishlist"""
    is_favorited = Favorite.objects.filter(user=request.user, product_id=product_id).exists()
    return JsonResponse({'is_favorited': is_favorited})


# --- ORDERS ---

@login_required
def orders_view(request):
    from django.utils import timezone
    from datetime import timedelta
    
    # Automatically update all user's orders based on creation time
    now = timezone.now()
    
    # Update to delivered if 2+ days old
    Order.objects.filter(
        user=request.user,
        status__in=['paid', 'shipped'],
        created_at__lte=now - timedelta(days=2)
    ).update(status='delivered')
    
    # Update to shipped if 1+ days old and still paid
    Order.objects.filter(
        user=request.user,
        status='paid',
        created_at__lte=now - timedelta(days=1)
    ).update(status='shipped')
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    from django.utils import timezone
    from datetime import timedelta
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Automatically update status based on creation time
    now = timezone.now()
    
    # If order is 2+ days old and not delivered, mark as delivered
    if order.status in ['paid', 'shipped'] and (now - order.created_at) >= timedelta(days=2):
        order.status = 'delivered'
        order.save()
    # If order is 1+ days old and still paid, mark as shipped
    elif order.status == 'paid' and (now - order.created_at) >= timedelta(days=1):
        order.status = 'shipped'
        order.save()
    
    items = order.items.select_related('variant__product').all()
    return render(request, 'order_detail.html', {'order': order, 'items': items})

# --- CART SECTION ---

def add_to_cart(request, product_id):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        
        if not variant_id:
            return redirect('product_detail', pk=product_id)

        cart = request.session.get('cart', {})

        if variant_id in cart:
            cart[variant_id]['quantity'] += 1
        else:
            cart[variant_id] = {'quantity': 1}

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart_page')

def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})
    
    if str(variant_id) in cart:
        del cart[str(variant_id)]
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart_page')


def decrease_quantity(request, variant_id):
    cart = request.session.get('cart', {})
    
    if str(variant_id) in cart:
        if cart[str(variant_id)]['quantity'] > 1:
            cart[str(variant_id)]['quantity'] -= 1
        else:
            del cart[str(variant_id)]
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart_page')


def cart_page(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for variant_id, item_data in cart.items():
        # Find the exact variant in the database
        variant = get_object_or_404(ProductVariant, id=variant_id) 
        
        # Calculate totals using your custom price() method
        item_price = variant.price()
        quantity = item_data['quantity']
        item_total = item_price * quantity
        cart_total += item_total
        
        # Try to get the first image for the cart thumbnail
        first_image = variant.product.images.first()
        image_url = first_image.get_url() if first_image else None
        
        cart_items.append({
            'variant': variant,
            'quantity': quantity,
            'item_total': item_total,
            'image_url': image_url,
        })

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'cart.html', context)


@login_required
def checkout(request):
    """Simple checkout entry point.

    - If cart is empty: redirect back to cart with a message.
    - If user has saved payment methods: redirect to payment methods.
    - Otherwise redirect to add a payment method.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart_page')

    methods = PaymentMethod.objects.filter(user=request.user)
    if methods.exists():
        return redirect('payment_methods')
    else:
        messages.info(request, 'Please add a payment method to continue.')
        return redirect('add_payment_method')


@login_required
def checkout_confirm(request):
    if request.method != 'POST':
        return redirect('payment_methods')

    pm_id = request.POST.get('payment_method')
    try:
        pm = PaymentMethod.objects.get(id=pm_id, user=request.user)
    except Exception:
        messages.error(request, 'Invalid payment method selected.')
        return redirect('payment_methods')

    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart_page')

    # calculate total and create order
    total = 0
    order = Order.objects.create(user=request.user, total_price=0)
    for variant_id, data in cart.items():
        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            continue
        qty = data.get('quantity', 1)
        price = variant.price()
        OrderItem.objects.create(order=order, variant=variant, quantity=qty, price=price)
        total += price * qty

    order.total_price = total
    order.status = 'paid'
    order.save()

    # clear session cart
    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, f'Order #{order.id} placed successfully using {pm.card_type.title()} ****{pm.card_number_last4}.')
    return redirect('orders')


@login_required
def checkout_address(request):
    """Handles selecting an address after a payment method is chosen.

    - If POST contains only `payment_method`: store it in session and render address list.
    - If POST contains `address`: finalize the order using stored payment method and chosen address.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart_page')

    # User submitted a payment method and now needs to choose address
    if request.method == 'POST' and request.POST.get('payment_method') and not request.POST.get('address'):
        pm_id = request.POST.get('payment_method')
        try:
            pm = PaymentMethod.objects.get(id=pm_id, user=request.user)
        except PaymentMethod.DoesNotExist:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('payment_methods')

        request.session['checkout_pm_id'] = pm.id
        addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
        return render(request, 'select_address.html', {'addresses': addresses})

    # Finalize order when address is posted
    if request.method == 'POST' and request.POST.get('address'):
        addr_id = request.POST.get('address')
        pm_id = request.session.get('checkout_pm_id') or request.POST.get('payment_method')

        # require consent flags
        if not (request.POST.get('accepted_terms') and request.POST.get('accepted_policy')):
            messages.error(request, 'Please read and accept the required documents before placing your order.')
            addresses = Address.objects.filter(user=request.user).order_by('-is_default', '-created_at')
            return render(request, 'select_address.html', {'addresses': addresses})

        try:
            pm = PaymentMethod.objects.get(id=pm_id, user=request.user)
        except Exception:
            messages.error(request, 'Invalid payment method.')
            return redirect('payment_methods')

        try:
            addr = Address.objects.get(id=addr_id, user=request.user)
        except Address.DoesNotExist:
            messages.error(request, 'Invalid address selected.')
            return redirect('addresses')

        # calculate total and create order (store shipping snapshot)
        total = 0
        order = Order.objects.create(
            user=request.user,
            total_price=0,
            shipping_full_name=addr.full_name,
            shipping_phone_number=addr.phone_number,
            shipping_street_address=addr.street_address,
            shipping_city=addr.city,
            shipping_postal_code=addr.postal_code,
            shipping_country=addr.country,
        )
        for variant_id, data in cart.items():
            try:
                variant = ProductVariant.objects.get(id=variant_id)
            except ProductVariant.DoesNotExist:
                continue
            qty = data.get('quantity', 1)
            price = variant.price()
            OrderItem.objects.create(order=order, variant=variant, quantity=qty, price=price)
            total += price * qty

        order.total_price = total
        order.status = 'paid'
        order.save()

        # clear session cart and checkout_pm
        request.session['cart'] = {}
        request.session.pop('checkout_pm_id', None)
        request.session.modified = True

        messages.success(request, f'✓ Order #{order.id} placed successfully! Using {pm.card_type.title()} ****{pm.card_number_last4} to {addr.full_name}, {addr.city}.')
        return redirect('order_detail', order_id=order.id)

    # If not POST, redirect back
    return redirect('payment_methods')

# --- PASSWORD RESET VIEWS ---

class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view using the custom form."""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password-reset/done/'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset done view."""
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view using the custom form."""
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/password-reset/complete/'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view."""
    template_name = 'accounts/password_reset_complete.html'


# --- COMPANY DASHBOARD VIEWS ---

def is_company(user):
    """Helper to check if a user is a company/seller."""
    if hasattr(user, 'profile'):
        return user.profile.role == 'company'
    return False

def company_required(view_func):
    """Decorator to ensure user is a company/seller."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access the company dashboard.")
            return redirect('login')
        if not is_company(request.user):
            messages.error(request, "You must be a company/seller to access this area.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

# views.py içinde company_dashboard fonksiyonunu bul ve değiştir:
@company_required
def company_dashboard(request):
    """Display company's active products."""
    # Sadece is_active=True olanları getir
    products = Product.objects.filter(company=request.user, is_active=True).order_by('-created_at')
    return render(request, 'company/dashboard.html', {'products': products})

@company_required
def company_add_product(request):
    """Form to add a new product with image and variant (size/stock) support."""
    if request.method == 'POST':
        try:
            brand_id = request.POST.get('brand')
            category_id = request.POST.get('category')
            
            brand = Brand.objects.get(id=brand_id)
            category = Category.objects.get(id=category_id) if category_id else None
            
            product = Product.objects.create(
                company=request.user,
                brand=brand,
                category=category,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                gender=request.POST.get('gender'),
                price=request.POST.get('price'),
                discount_percent=request.POST.get('discount_percent', 0),
                material=request.POST.get('material'),
            )

            # 1. Resim Kaydetme
            image_file = request.FILES.get('image')
            if image_file:
                ProductImage.objects.create(product=product, image=image_file, is_primary=True)

            # 2. Varyant (Beden, Renk ve Stok) Kaydetme
            color = request.POST.get('color', 'Standard')
            sizes = request.POST.getlist('sizes') # İşaretlenen bedenlerin listesi
            
            for size in sizes:
                # O bedene ait stoğu alıyoruz (stock_36, stock_37 vb.)
                stock_val = int(request.POST.get(f'stock_{size}', 0))
                # Benzersiz bir SKU üretiyoruz
                sku = f"{product.id}-{size}-{color[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
                
                ProductVariant.objects.create(
                    product=product,
                    sku=sku,
                    size=size,
                    color=color,
                    stock=stock_val,
                    is_active=True
                )

            messages.success(request, f"Product '{product.name}' and variants added successfully!")
            return redirect('company_dashboard')
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
    
    brands = Brand.objects.all()
    categories = Category.objects.all()
    # Varsayılan ayakkabı bedenleri
    all_sizes = ["36", "37", "38", "39", "40", "41", "42", "43"]
    
    return render(request, 'company/add_product.html', {
        'brands': brands,
        'categories': categories,
        'all_sizes': all_sizes,
    })

@company_required
def company_edit_product(request, product_id):
    """Form to edit a product and its variants."""
    product = get_object_or_404(Product, id=product_id, company=request.user)
    all_sizes = ["36", "37", "38", "39", "40", "41", "42", "43"]
    
    if request.method == 'POST':
        try:
            brand_id = request.POST.get('brand')
            category_id = request.POST.get('category')
            
            product.brand = Brand.objects.get(id=brand_id)
            product.category = Category.objects.get(id=category_id) if category_id else None
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.gender = request.POST.get('gender')
            product.price = request.POST.get('price')
            product.discount_percent = request.POST.get('discount_percent', 0)
            product.material = request.POST.get('material')
            product.save()
            
            # Yeni resim yükleme kontrolü
            new_image = request.FILES.get('new_image')
            if new_image:
                is_primary = not product.images.exists()
                ProductImage.objects.create(product=product, image=new_image, is_primary=is_primary)
            
            # Varyantları Güncelleme
            color = request.POST.get('color', 'Standard')
            submitted_sizes = request.POST.getlist('sizes')
            
            for size in all_sizes:
                variant = ProductVariant.objects.filter(product=product, size=size).first()
                
                if size in submitted_sizes:
                    stock_val = int(request.POST.get(f'stock_{size}', 0))
                    if variant:
                        # Varyant varsa güncelle
                        variant.stock = stock_val
                        variant.color = color
                        variant.is_active = True
                        variant.save()
                    else:
                        # Varyant yoksa yeni oluştur
                        sku = f"{product.id}-{size}-{color[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
                        ProductVariant.objects.create(
                            product=product, sku=sku, size=size, color=color, stock=stock_val, is_active=True
                        )
                else:
                    # Beden işareti kaldırıldıysa, pasif yap ve stoğu sıfırla (Silmek sipariş hatasına yol açabilir)
                    if variant:
                        variant.is_active = False
                        variant.stock = 0
                        variant.save()
            
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('company_dashboard')
        except Exception as e:
            messages.error(request, f"Error updating product: {str(e)}")
    
    # Template'e gönderilecek mevcut varyant verilerini hazırla
    existing_variants = {v.size: v for v in product.variants.all()}
    variants_data = []
    default_color = product.variants.first().color if product.variants.exists() else ''
    
    for size in all_sizes:
        var = existing_variants.get(size)
        variants_data.append({
            'size': size,
            'is_active': var.is_active if var else False,
            'stock': var.stock if var else '',
        })
        
    brands = Brand.objects.all()
    categories = Category.objects.all()
    return render(request, 'company/edit_product.html', {
        'product': product,
        'brands': brands,
        'categories': categories,
        'variants_data': variants_data,
        'default_color': default_color,
    })

@company_required
def company_delete_product(request, product_id):
    """
    Soft-delete a product to preserve order history.
    Instead of deleting from DB, sets is_active=False and cancels pending orders.
    """
    product = get_object_or_404(Product, id=product_id, company=request.user)
    
    if request.method == 'POST':
        product_name = product.name
        
        # 1. Ürünü ve varyantlarını siteden gizle (Soft Delete)
        product.is_active = False
        product.save()
        
        product.variants.update(is_active=False, stock=0)
        
        # 2. Bu ürünü içeren ve henüz teslim edilmemiş (pending, paid, shipped) siparişleri bul
        # Sadece bu ürünün olduğu siparişleri etkilemek istiyoruz
        affected_orders = Order.objects.filter(
            items__variant__product=product,
            status__in=['pending', 'paid', 'shipped']
        ).distinct()
        
        # 3. Siparişlerin durumunu 'cancelled' olarak güncelle
        for order in affected_orders:
            order.status = 'cancelled'
            order.save()
            
        messages.success(request, f"Product '{product_name}' has been removed from the store and active orders cancelled.")
        return redirect('company_dashboard')
    
    return render(request, 'company/delete_product.html', {'product': product})


# --- COMPANY IMAGE MANAGEMENT (YENI EKLENDI) ---

@company_required
def company_delete_image(request, image_id):
    """Delete a product image via AJAX."""
    if request.method == 'POST':
        try:
            image = ProductImage.objects.get(id=image_id, product__company=request.user)
            image.delete()
            return JsonResponse({'status': 'success', 'message': 'Image deleted successfully'})
        except ProductImage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@company_required
def company_set_primary_image(request, image_id):
    """Set an image as primary for the product via AJAX."""
    if request.method == 'POST':
        try:
            image = ProductImage.objects.get(id=image_id, product__company=request.user)
            # Remove primary flag from all images of this product
            image.product.images.update(is_primary=False)
            # Set this image as primary
            image.is_primary = True
            image.save()
            return JsonResponse({'status': 'success', 'message': 'Primary image updated'})
        except ProductImage.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)