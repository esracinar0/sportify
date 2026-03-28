from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .models import Product, UserProfile, Favorite, Order, Address, PaymentMethod, CartItem, Brand
from .forms import LoginForm, RegisterForm, UserUpdateForm, UserProfileForm, CustomPasswordResetForm, CustomSetPasswordForm

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
    return render(request, 'payment_methods.html', {'methods': methods})

@login_required
def add_payment_method(request):
    if request.method == 'POST':
        card_num = request.POST.get('card_number')
        PaymentMethod.objects.create(
            user=request.user,
            card_holder_name=request.POST.get('card_holder'),
            card_number_last4=card_num.replace(' ', '')[-4:] if card_num else "0000",
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
        return redirect('addresses')
    return render(request, 'add_address.html')

# --- USER PROFILE SECTIONS ---

@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user)
    return render(request, 'favorites.html', {'favorites': favorites})

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})

# --- CART SECTION ---

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import ProductVariant # Make sure this matches your models file import path

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