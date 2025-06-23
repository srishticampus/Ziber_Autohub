# hub/views.py
import os
import joblib
import re
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db import transaction # Import transaction for atomic operations

from .models import UserProfile, Car, ServiceBooking, JobVacancy, JobApplication, PreBooking, Accessory # Import Accessory
from .models import Cart, CartItem, Order, OrderItem,LaunchRegistration # Explicitly import Cart and Order related models
from admin_panel.models import UpcomingLaunch

from .forms import (
    # UserRegistrationForm, # Assuming this is handled in register_user directly
    JobApplicationForm, JobVacancyForm, CarDetailsForm, PreBookingForm, UsedCarFilterForm, UsedCarForm,
    AddToCartForm, CheckoutForm,LaunchRegistrationForm # Import the new forms
)
from datetime import timedelta, date
from django.utils import timezone # Make sure timezone is imported for any date operations

@login_required
def index(request):
    new_cars = Car.objects.filter(is_new=True).order_by('-created_at')[:3]
    old_cars = Car.objects.filter(is_new=False).order_by('-created_at')[:3]
    # Optionally, fetch some accessories for the homepage
    featured_accessories = Accessory.objects.order_by('-created_at')[:3] 
    return render(request, 'index.html', {
        'new_cars': new_cars, 
        'old_cars': old_cars,
        'featured_accessories': featured_accessories
    })

def demo(request):
    """
    Renders the 'demo' page which serves as the main landing/home page,
    featuring dynamic banner backgrounds and upcoming car launches.
    """
    # Fetch upcoming car launches to display in the dedicated section
    # Order by launch date to show the soonest launches first
    upcoming_launches = UpcomingLaunch.objects.all().order_by('launch_date', 'launch_time_start')

    context = {
        'upcoming_launches': upcoming_launches,
        # 'featured_new_cars' and 'latest_news_cars' are no longer passed here
        # as the 'demo.html' template now handles these sections with static
        # content or data from 'upcoming_launches'.
    }
    return render(request, 'demo.html', context)


def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        age = request.POST['age']
        place = request.POST['place']
        contact_number = request.POST['contact_number']
        image = request.FILES.get('user_image')
        gender = request.POST['gender']

        errors = {}

        # Username validation
        if User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists!"
        if username.isdigit(): # Check if username consists only of digits
            errors['username'] = "Username cannot consist only of numbers."
        if not username:
            errors['username'] = "Username is required."


        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Invalid email format!"
        if User.objects.filter(email=email).exists():
            errors['email'] = "Email already exists!"
        if not email:
            errors['email'] = "Email is required."

        # Password validation
        if password != confirm_password:
            errors['password'] = "Passwords do not match!"
        # Password complexity: at least one uppercase, one number, one symbol
        if not re.search(r'[A-Z]', password):
            errors['password_uppercase'] = "Password must contain at least one uppercase letter."
        if not re.search(r'\d', password):
            errors['password_digit'] = "Password must contain at least one number."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): # Common symbols
            errors['password_symbol'] = "Password must contain at least one symbol."
        if len(password) < 8: # Example: minimum length
            errors['password_length'] = "Password must be at least 8 characters long."
        if not password:
            errors['password'] = "Password is required."


        # Age validation
        try:
            age = int(age)
            if age < 0:
                errors['age'] = "Age cannot be negative."
        except ValueError:
            errors['age'] = "Age must be a number."
        if not age: # This will catch empty strings, but also age 0, which might be valid.
                     # Consider `if not str(age).strip():` for empty string check.
            errors['age'] = "Age is required."

        # Place validation
        if not re.fullmatch(r'[a-zA-Z\s]+', place): # Only letters and spaces
            errors['place'] = "Place can only contain letters and spaces."
        if not place:
            errors['place'] = "Place is required."

        # Contact number validation
        if not contact_number.isdigit():
            errors['contact_number'] = "Contact number can only contain digits."
        if len(contact_number) != 10:
            errors['contact_number'] = "Contact number must be exactly 10 digits long."
        if UserProfile.objects.filter(contact_number=contact_number).exists():
            errors['contact_number'] = "This contact number is already registered!"
        if not contact_number:
            errors['contact_number'] = "Contact number is required."

        # Image validation
        if not image:
            errors['user_image'] = "User image is required."


        if errors:
            # Pass back the original POST data to re-populate the form
            return render(request, 'register.html', {'errors': errors, 'form_data': request.POST})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = True
        user.save()

        UserProfile.objects.create(
            user=user,
            age=age,
            place=place,
            contact_number=contact_number,
            image=image,
            gender=gender
        )

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('hub:login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Basic validations for login fields
        if not username:
            messages.error(request, "Username is required.")
            return render(request, 'login.html', {'username_value': username})
        if not password:
            messages.error(request, "Password is required.")
            return render(request, 'login.html', {'username_value': username})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, "You have been successfully logged in.")
            if user.is_superuser:
                return redirect('admin_panel:admin_dashboard')
            return redirect('hub:home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html', {'username_value': request.POST.get('username', '')})


def logout_user(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('hub:demo')


def car_list(request):
    query = request.GET.get('q', '')
    year_filter = request.GET.get('year', '')
    brand_filter = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    cars = Car.objects.all().order_by('-year', 'brand')

    # Apply filters
    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )

    if year_filter:
        cars = cars.filter(year=year_filter)

    if brand_filter:
        cars = cars.filter(brand=brand_filter)

    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            cars = cars.filter(price__gte=min_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid minimum price format.")
            return redirect('hub:car_list') # Redirect to clear invalid state

    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            cars = cars.filter(price__lte=max_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid maximum price format.")
            return redirect('hub:car_list') # Redirect to clear invalid state

    # Get unique years and brands for filter dropdowns
    years = Car.objects.values_list('year', flat=True).distinct().order_by('-year')
    brands = Car.objects.values_list('brand', flat=True).distinct().order_by('brand')

    context = {
        'cars': cars,
        'query': query,
        'years': years,
        'brands': brands,
        'selected_year': year_filter,
        'selected_brand': brand_filter,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'car_list.html', context)

def new_car_list(request):
    cars = Car.objects.filter(is_new=True)
    query = request.GET.get('q')
    selected_brand = request.GET.get('brand')
    selected_year = request.GET.get('year')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )

    if selected_brand:
        cars = cars.filter(brand=selected_brand)

    if selected_year:
        cars = cars.filter(year=selected_year)

    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            cars = cars.filter(price__gte=min_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid minimum price format.")
            return redirect('hub:new_car_list')

    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            cars = cars.filter(price__lte=max_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid maximum price format.")
            return redirect('hub:new_car_list')

    brands = Car.objects.filter(is_new=True).values_list('brand', flat=True).distinct().order_by('brand')
    years = Car.objects.filter(is_new=True).values_list('year', flat=True).distinct().order_by('-year')

    context = {
        'cars': cars,
        'query': query,
        'brands': brands,
        'years': years,
        'selected_brand': selected_brand,
        'selected_year': selected_year,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'new_car_list.html', context)


def used_car_list(request):
    query = request.GET.get('q', '')
    year_filter = request.GET.get('year', '')
    brand_filter = request.GET.get('brand', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_kms = request.GET.get('min_kms', '')
    max_kms = request.GET.get('max_kms', '')

    cars = Car.objects.filter(is_new=False).order_by('-year', 'brand')

    # Apply filters
    if query:
        cars = cars.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )

    if year_filter:
        cars = cars.filter(year=year_filter)

    if brand_filter:
        cars = cars.filter(brand=brand_filter)

    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            cars = cars.filter(price__gte=min_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid minimum price format.")
            return redirect('hub:used_car_list')

    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            cars = cars.filter(price__lte=max_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid maximum price format.")
            return redirect('hub:used_car_list')

    if min_kms:
        cars = cars.filter(kms_driven__gte=min_kms)

    if max_kms:
        cars = cars.filter(kms_driven__lte=max_kms)

    # Get unique years and brands for filter dropdowns for used cars
    years = Car.objects.filter(is_new=False).values_list('year', flat=True).distinct().order_by('-year')
    brands = Car.objects.filter(is_new=False).values_list('brand', flat=True).distinct().order_by('brand')

    context = {
        'cars': cars,
        'query': query,
        'years': years,
        'brands': brands,
        'selected_year': year_filter,
        'selected_brand': brand_filter,
        'min_price': min_price,
        'max_price': max_price,
        'min_kms': min_kms,
        'max_kms': max_kms,
        'form': UsedCarFilterForm(request.GET), # Pass the form for rendering filters
    }

    return render(request, 'used_car_list.html', context)

@login_required
def car_detail(request, pk):
    car = get_object_or_404(Car, pk=pk)
    
    # Calculate pre-booking cost (5% of the car price)
    pre_booking_cost = car.price * Decimal('0.05')
    
    # Instantiate AddToCartForm for the quantity input
    form = AddToCartForm()

    context = {
        'car': car,
        'pre_booking_cost': pre_booking_cost,
        'form': form, # Pass the form to the template
    }
    return render(request, 'car_detail.html', context)

#  Accessory list view
def accessory_list(request):
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    accessories = Accessory.objects.all().order_by('name')

    if query:
        accessories = accessories.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    if category_filter:
        accessories = accessories.filter(category=category_filter)

    if min_price:
        try:
            min_price_decimal = Decimal(min_price)
            accessories = accessories.filter(price__gte=min_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid minimum price format.")
            return redirect('hub:accessory_list')

    if max_price:
        try:
            max_price_decimal = Decimal(max_price)
            accessories = accessories.filter(price__lte=max_price_decimal)
        except (ValueError, TypeError):
            messages.error(request, "Invalid maximum price format.")
            return redirect('hub:accessory_list')

    categories = Accessory.objects.values_list('category', flat=True).distinct().order_by('category')

    context = {
        'accessories': accessories,
        'query': query,
        'categories': categories,
        'selected_category': category_filter,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'accessory_list.html', context)

# Accessory detail view
@login_required
def accessory_detail(request, pk):
    accessory = get_object_or_404(Accessory, pk=pk)
    form = AddToCartForm() # Form for adding to cart
    context = {
        'accessory': accessory,
        'form': form,
    }
    return render(request, 'accessory_detail.html', context)


@login_required
def add_to_cart(request, pk, product_type):
    """
    Adds a car or accessory to the user's cart.
    `product_type` can be 'car' or 'accessory'.
    """
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            user_cart, created = Cart.objects.get_or_create(user=request.user)

            product = None
            if product_type == 'car':
                product = get_object_or_404(Car, pk=pk)
                if quantity > 1:
                    messages.error(request, "You can only add one car at a time to the cart.")
                    return redirect('hub:car_detail', pk=pk)
            elif product_type == 'accessory':
                product = get_object_or_404(Accessory, pk=pk)
            else:
                messages.error(request, "Invalid product type.")
                return redirect('hub:home') # Or a more appropriate fallback

            if product:
                # Check if item already exists in cart
                if product_type == 'car':
                    cart_item_query = CartItem.objects.filter(cart=user_cart, car=product)
                else: # accessory
                    cart_item_query = CartItem.objects.filter(cart=user_cart, accessory=product)

                cart_item_exists = cart_item_query.exists()

                if cart_item_exists:
                    cart_item = cart_item_query.first()
                    # For cars, quantity is always 1, so no increment needed
                    if product_type == 'car':
                        messages.warning(request, f"{product.name} is already in your cart.")
                    else: # For accessories, increment quantity
                        if cart_item.quantity + quantity <= product.stock:
                            cart_item.quantity += quantity
                            cart_item.save()
                            messages.success(request, f"Added {quantity} more {product.name} to your cart.")
                        else:
                            messages.error(request, f"Only {product.stock} of {product.name} available. You have {cart_item.quantity} in cart, cannot add {quantity}.")
                else:
                    # New item
                    if quantity <= product.stock:
                        CartItem.objects.create(
                            cart=user_cart,
                            car=product if product_type == 'car' else None,
                            accessory=product if product_type == 'accessory' else None,
                            quantity=quantity
                        )
                        messages.success(request, f"Added {quantity} x {product.name} to your cart.")
                    else:
                        messages.error(request, f"Only {product.stock} of {product.name} available.")

                return redirect('hub:view_cart')
        else: # Form is not valid
            # If the quantity is invalid, redirect back to the product detail page
            if product_type == 'car':
                return redirect('hub:car_detail', pk=pk)
            elif product_type == 'accessory':
                return redirect('hub:accessory_detail', pk=pk)
    
    messages.error(request, "Invalid request to add item to cart.")
    return redirect('hub:home') # Fallback

@login_required
def view_cart(request):
    """
    Displays the user's cart. If no cart exists for the user, one is created.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    total_price = cart.get_total_price() # Use the method from the Cart model

    if created or not cart_items.exists():
        messages.info(request, "Your cart is currently empty.")

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, "Invalid quantity provided.")
            return redirect('hub:view_cart')

        product = cart_item.get_product()
        if not product:
            messages.error(request, "Product associated with this cart item no longer exists.")
            cart_item.delete() # Clean up invalid item
            return redirect('hub:view_cart')

        # For cars, quantity should always be 1
        if cart_item.car and quantity != 1:
            messages.error(request, "Quantity for cars cannot be changed. Please remove and re-add if necessary.")
            return redirect('hub:view_cart')
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        elif quantity > product.stock:
            messages.error(request, f"Only {product.stock} of {product.name} available in stock.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")

    return redirect('hub:view_cart')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    product_name = cart_item.get_product().name if cart_item.get_product() else "item"
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart.")
    return redirect('hub:view_cart')

@login_required
def checkout(request):
    user_cart = get_object_or_404(Cart, user=request.user)
    cart_items = user_cart.items.all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('hub:view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): # Ensure atomicity for order creation and stock update
                # Create the Order
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=f"{form.cleaned_data['address_line1']}, "
                                     f"{form.cleaned_data.get('address_line2', '')}, "
                                     f"{form.cleaned_data['city']}, {form.cleaned_data['state']}, "
                                     f"{form.cleaned_data['zip_code']}, {form.cleaned_data['country']}",
                    payment_method=form.cleaned_data['payment_method'],
                    # total_amount will be calculated after order items are created
                )

                order_total = Decimal('0.00')

                for item in cart_items:
                    product = item.get_product()
                    if not product:
                        # This scenario should ideally be prevented by cart_item.clean(),
                        # but as a safeguard, handle if product became None
                        messages.error(request, f"A product in your cart could not be found. Please review your cart.")
                        transaction.set_rollback(True) # Rollback the transaction
                        return redirect('hub:view_cart')

                    # Double-check stock before creating order item
                    if item.quantity > product.stock:
                        messages.error(request, f"Insufficient stock for {product.name}. Only {product.stock} available.")
                        transaction.set_rollback(True) # Rollback the transaction
                        return redirect('hub:view_cart')
                    
                    OrderItem.objects.create(
                        order=order,
                        car=item.car,
                        accessory=item.accessory,
                        quantity=item.quantity,
                        price=item.get_item_price() # Price at the time of order
                    )
                    
                    # Decrement stock
                    product.stock -= item.quantity
                    product.save()

                    order_total += item.get_total_price()

                order.total_amount = order_total
                order.save() # Save order with calculated total_amount

                user_cart.items.all().delete() # Clear the cart

                messages.success(request, "Your order has been placed successfully!")
                # Redirect to payment success page, perhaps showing order ID
                return redirect('hub:payment_success', order_id=order.id) # Pass order_id to success page
        else:
            messages.error(request, "Please correct the errors in your shipping details.")
            # Form will be re-rendered with errors below
    else:
        # Pre-fill form if user has a profile with address/phone
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            user_profile = request.user.profile
            initial_data['full_name'] = f"{request.user.first_name} {request.user.last_name}" if request.user.first_name and request.user.last_name else request.user.username
            initial_data['email'] = request.user.email
            # You might need to map user_profile.place to city/state/country more intelligently
            # For simplicity, assume place is a general address here or add more fields to UserProfile
            # initial_data['address_line1'] = user_profile.place # Example
            # initial_data['contact_number'] = user_profile.contact_number # Not in CheckoutForm currently
        form = CheckoutForm(initial=initial_data)

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': user_cart.get_total_price() # Always recalculate for display
    })

@login_required
def buy_now(request, pk, product_type):
    """
    Handles immediate purchase of a single car or accessory.
    Adds the item to the cart and redirects directly to checkout.
    """
    if product_type == 'car':
        product = get_object_or_404(Car, pk=pk)
        if product.is_new:
            # If it's a new car, redirect to pre-booking flow
            return redirect('hub:pre_book_car', car_id=pk)
        
        # For used cars, proceed to add to cart and checkout
        item_name = product.name
        redirect_url_on_fail = 'hub:car_detail'
    elif product_type == 'accessory':
        product = get_object_or_404(Accessory, pk=pk)
        item_name = product.name
        redirect_url_on_fail = 'hub:accessory_detail'
    else:
        messages.error(request, "Invalid product type for Buy Now.")
        return redirect('hub:home')

    user_cart, created = Cart.objects.get_or_create(user=request.user)

    # Check for existing item in cart
    if product_type == 'car':
        existing_cart_item_query = CartItem.objects.filter(cart=user_cart, car=product)
    else: # accessory
        existing_cart_item_query = CartItem.objects.filter(cart=user_cart, accessory=product)
    
    if existing_cart_item_query.exists():
        messages.info(request, f"{item_name} is already in your cart. Redirecting to checkout.")
        return redirect('hub:checkout')

    # If not in cart, add it
    if product.stock > 0:
        CartItem.objects.create(
            cart=user_cart,
            car=product if product_type == 'car' else None,
            accessory=product if product_type == 'accessory' else None,
            quantity=1 # Buy Now typically means 1 item initially
        )
        messages.success(request, f"Added {item_name} to your cart. Proceeding to checkout.")
        return redirect('hub:checkout')
    else:
        messages.error(request, f"Sorry, {item_name} is out of stock.")
        # Redirect back to the detail page if out of stock
        if product_type == 'car':
            return redirect('hub:car_detail', pk=pk)
        else: # accessory
            return redirect('hub:accessory_detail', pk=pk)

# The process_order view is now deprecated as checkout handles order creation directly
# @login_required
# def process_order(request):
#     # This view is no longer needed as `checkout` handles order creation.
#     # You can remove its URL pattern and the view definition if desired.
#     messages.error(request, "This page is deprecated.")
#     return redirect('hub:home')


@login_required
def payment(request):
    # This view is a placeholder. In a real app, you'd integrate a payment gateway.
    # It might display the order summary before payment.
    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        order = get_object_or_404(Order, pk=order_id, user=request.user)

    return render(request, 'payment.html', {'order': order})

@login_required
def payment_success(request, order_id=None):
    # Retrieve order details if passed, or just show a generic success
    order = None
    if order_id:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, 'payment_success.html', {'order': order})

@login_required
def my_bookings(request):
    # This view seems to be for old service booking form. The `book_service` is the new one.
    # It seems to be showing ServiceBooking instances, so it should be fine as a historical view.
    bookings = ServiceBooking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'my_bookings.html', {'bookings': bookings})

def job_list(request):
    jobs = JobVacancy.objects.filter(is_active=True).order_by('-posted_at')
    return render(request, 'job_list.html', {'jobs': jobs})

@login_required
def apply_job(request, pk):
    job = get_object_or_404(JobVacancy, pk=pk, is_active=True)

    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('hub:job_list')

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('hub:job_list')
    else:
        form = JobApplicationForm()

    return render(request, 'apply_job.html', {'form': form, 'job': job})

@login_required
def create_job_vacancy(request):
    if not request.user.is_staff:
        # Instead of PermissionDenied, redirect with a message
        messages.error(request, "You do not have permission to access this page.")
        return redirect('hub:home')

    if request.method == 'POST':
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy created!')
            return redirect('hub:job_list')
    else:
        form = JobVacancyForm()

    return render(request, 'create_job_vacancy.html', {'form': form}) # Point to a dedicated template

def news(request):
    return render(request, 'news_details.html')

def products(request):
    # This view likely serves as a "new releases" or general products page.
    # Consider renaming it to 'new_releases' for clarity if that's its sole purpose.
    new_cars = Car.objects.filter(is_new=True).order_by('-created_at')
    return render(request, 'p_details.html', {'new_cars': new_cars})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date') # Changed from created_at
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')
    return render(request, 'my_applications.html', {'applications': applications})

# Load model once
model_path = os.path.join(os.path.dirname(__file__), 'ml_model/random_forest_regression_model.pkl')
try:
    model = joblib.load(model_path)
except FileNotFoundError:
    model = None # Handle case where model file is not found
    print(f"Warning: ML model not found at {model_path}. Prediction functionality will be unavailable.")

# StaffRequiredMixin definition (not used in views directly, but good to keep if it's imported elsewhere)
class StaffRequiredMixin:
    """Mixin to ensure the user is a staff member."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

def predict_price(request):
    if not model:
        messages.error(request, "The car price prediction model is currently unavailable. Please try again later.")
        return render(request, 'predict_form.html', {'form': CarDetailsForm(), 'model_unavailable': True})

    if request.method == 'POST':
        form = CarDetailsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Preprocessing same as training data
            # Use current year for car age calculation
            car_age = date.today().year - data['year']
            fuel_type = data['fuel_type']
            fuel_type_cng = 1 if fuel_type == 'CNG' else 0
            fuel_type_diesel = 1 if fuel_type == 'Diesel' else 0
            fuel_type_petrol = 1 if fuel_type == 'Petrol' else 0

            seller_type = data['seller_type']
            seller_type_dealer = 1 if seller_type == 'Dealer' else 0
            seller_type_individual = 1 if seller_type == 'Individual' else 0

            transmission = data['transmission']
            transmission_manual = 1 if transmission == 'Manual' else 0
            transmission_automatic = 1 if transmission == 'Automatic' else 0

            # Final input vector with 11 features in order
            features = [[
                data['present_price'],
                data['kms_driven'],
                data['owner'],
                car_age,
                fuel_type_cng,
                fuel_type_diesel,
                fuel_type_petrol,
                seller_type_dealer,
                seller_type_individual,
                transmission_automatic,
                transmission_manual
            ]]

            # Prediction
            predicted_price = model.predict(features)[0]

            return render(request, 'predict_result.html', {
                'price': round(predicted_price, 2)
            })
    else:
        form = CarDetailsForm()

    return render(request, 'predict_form.html', {'form': form})

@login_required
def pre_book_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id, is_new=True) # Ensure only new cars can be pre-booked
    existing_booking = PreBooking.objects.filter(user=request.user, car=car, status__in=['Booked', 'Pending']).exists()

    if existing_booking:
        messages.error(request, 'You have already pre-booked this car, or a booking is pending.')
        return redirect('hub:my_prebookings') # Or a more appropriate page, e.g., car_detail

    if request.method == 'POST':
        form = PreBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car # <--- THIS LINE IS CRUCIAL TO FIX THE IntegrityError
            # delivery_date is now handled in the model's save method, no need to set here explicitly unless overriding
            booking.save()
            messages.success(request, f'Successfully pre-booked {car.brand} {car.model}! Proceeding to payment.')
            return redirect('hub:payment') # Redirect to payment page as requested
    else:
        form = PreBookingForm()

    return render(request, 'prebook_car.html', {'form': form, 'car': car})

@login_required
def my_prebookings(request):
    bookings = PreBooking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'my_prebookings.html', {'bookings': bookings})

@login_required
def add_used_car(request):
    if request.method == 'POST':
        form = UsedCarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save()
            return redirect('hub:used_car_list')
    else:
        form = UsedCarForm()
    return render(request, 'add_used_car.html', {'form': form})

# @login_required
# def my_chats(request):
#    # Get all unique conversations where the user is either sender or receiver
#    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))

#    # Get distinct (car, other_user) combinations
#    threads = {}
#    for msg in messages:
#        car = msg.car
#        other_user = msg.receiver if msg.sender == request.user else msg.sender
#        key = (car.id, other_user.id)
#        if key not in threads:
#            threads[key] = {
#                'car': car,
#                'other_user': other_user,
#                'last_message': msg
#            }

#    return render(request, 'my_chats.html', {'threads': threads.values()})

@login_required
def book_service(request):
    # Find user's delivered new cars
    delivered_cars_ids = PreBooking.objects.filter(
        user=request.user,
        car__is_new=True,
        status="Delivered"
    ).values_list('car_id', flat=True)

    eligible_cars = Car.objects.filter(id__in=delivered_cars_ids)

    # Prepare initial available service types for all cars
    # This dictionary will store available services per car ID
    car_service_options = {}
    for car in eligible_cars:
        # Get the latest service type booked for this car by the current user
        # We need to consider the order of services to determine the 'latest'
        service_order_map = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}

        # Get all service bookings for this car and user, ordered by their numeric value
        booked_services_for_car = ServiceBooking.objects.filter(
            user=request.user,
            car=car
        ).order_by('booked_at')

        # Find the highest ordered service type that has been booked
        latest_service_order_num = 0
        for service_booking in booked_services_for_car:
            if service_booking.service_type in service_order_map:
                current_service_num = service_order_map[service_booking.service_type]
                if current_service_num > latest_service_order_num:
                    latest_service_order_num = current_service_num

        next_service_type = None
        # Determine the next service type based on the last booked service's order number
        for service_type_key, order_num in service_order_map.items():
            if order_num == latest_service_order_num + 1:
                next_service_type = service_type_key
                break

        if next_service_type:
            car_service_options[car.id] = [next_service_type] # Only the next service is available
        else:
            car_service_options[car.id] = [] # No services available if all are done or no next one found


    # Initialize selected values for form re-population on error
    selected_car_id = request.POST.get('car') if request.method == 'POST' else None
    selected_service_type = request.POST.get('service_type') if request.method == 'POST' else None
    selected_description = request.POST.get('description') if request.method == 'POST' else None


    if request.method == 'POST':
        car_id = request.POST.get('car')
        service_type = request.POST.get('service_type')
        description = request.POST.get('description')

        # Basic validation: Check if car_id and service_type are provided
        if not car_id or not service_type:
            messages.error(request, "Please select a car and service type.")
            # Re-render with existing data for user convenience
            return render(request, 'book_service.html', {
                'eligible_cars': eligible_cars,
                'car_service_options': json.dumps(car_service_options), # Pass as JSON string
                'selected_car_id': selected_car_id,
                'selected_service_type': selected_service_type,
                'selected_description': selected_description,
            })

        try:
            car = Car.objects.get(id=car_id)

            # Re-validate service type based on actual available services for this car
            # Convert car_id to int for dictionary lookup
            if service_type not in car_service_options.get(int(car_id), []):
                messages.error(request, f"'{service_type}' service is not the next available service for {car.name} {car.model}. Please check your bookings.")
                return render(request, 'book_service.html', {
                    'eligible_cars': eligible_cars,
                    'car_service_options': json.dumps(car_service_options), # Pass as JSON string
                    'selected_car_id': selected_car_id,
                    'selected_service_type': selected_service_type,
                    'selected_description': selected_description,
                })

            ServiceBooking.objects.create(
                user=request.user,
                car=car,
                service_type=service_type,
                description=description
            )
            messages.success(request, "Service booked successfully!")
            return redirect('hub:my_service_bookings')

        except Car.DoesNotExist:
            messages.error(request, "Selected car does not exist.")
            return redirect('hub:book_service') # Redirect to clear invalid state
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('hub:book_service')

    return render(request, 'book_service.html', {
        'eligible_cars': eligible_cars,
        'car_service_options': json.dumps(car_service_options), # Pass as JSON string
        'selected_car_id': selected_car_id, # Pass initial selected car ID
        'selected_service_type': selected_service_type, # Pass initial selected service type
        'selected_description': selected_description, # Pass initial description
    })

@login_required
def my_service_bookings(request):
    services = ServiceBooking.objects.filter(user=request.user).order_by('-booked_at') # Order by newest first
    return render(request, 'my_services.html', {'services': services})


@csrf_exempt
def book_service_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        car_id = data.get('car_id')
        service_type = data.get('service_type')
        description = data.get('description')

        try:
            car = Car.objects.get(id=car_id)

            # --- API-specific Validation for sequential services ---
            service_order_map = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}
            booked_services_for_car = ServiceBooking.objects.filter(
                user=request.user,
                car=car
            ).order_by('booked_at')

            latest_service_order_num = 0
            for service_booking in booked_services_for_car:
                if service_booking.service_type in service_order_map:
                    current_service_num = service_order_map[service_booking.service_type]
                    if current_service_num > latest_service_order_num:
                        latest_service_order_num = current_service_num

            # Determine expected next service based on current bookings
            expected_next_service = None
            for s_type, s_num in service_order_map.items():
                if s_num == latest_service_order_num + 1:
                    expected_next_service = s_type
                    break

            if service_type != expected_next_service:
                return JsonResponse({"success": False, "message": f"'{service_type}' service is not the next expected service. Expected: '{expected_next_service}'."})
            # --- End API-specific Validation ---

            ServiceBooking.objects.create(
                user=request.user,
                car=car,
                service_type=service_type,
                description=description
            )
            return JsonResponse({"success": True, "message": "Service booked successfully!"}) # Added message

        except Car.DoesNotExist:
            return JsonResponse({"success": False, "message": "Selected car does not exist."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"success": False, "message": "Invalid request method"})

# NEW: service_chatbot view
@login_required
def service_chatbot(request):
    # For test drives, show all available new cars
    available_cars = Car.objects.filter(is_new=True).values('id', 'name', 'model')
    
    # For service booking, show only delivered cars
    delivered_cars_ids = PreBooking.objects.filter(
        user=request.user,
        car__is_new=True,
        status="Delivered"
    ).values_list('car_id', flat=True)

    eligible_cars_queryset = Car.objects.filter(id__in=delivered_cars_ids)
    
    # Convert querysets to lists of dictionaries for JSON serialization
    test_drive_cars = list(available_cars)
    eligible_cars = list(eligible_cars_queryset.values('id', 'name', 'model'))

    # Prepare service options for service booking
    car_service_options = {}
    service_order_map = {'1st': 1, '2nd': 2, '3rd': 3, '4th': 4}

    for car in eligible_cars_queryset:
        booked_services_for_car = ServiceBooking.objects.filter(
            user=request.user,
            car=car
        ).order_by('booked_at')

        latest_service_order_num = 0
        for service_booking in booked_services_for_car:
            if service_booking.service_type in service_order_map:
                current_service_num = service_order_map[service_booking.service_type]
                if current_service_num > latest_service_order_num:
                    latest_service_order_num = current_service_num

        next_service_type = None
        for service_type_key, order_num in service_order_map.items():
            if order_num == latest_service_order_num + 1:
                next_service_type = service_type_key
                break

        if next_service_type:
            car_service_options[car.id] = [next_service_type]
        else:
            car_service_options[car.id] = []

    context = {
        'eligible_cars': json.dumps(eligible_cars),
        'test_drive_cars': json.dumps(test_drive_cars),
        'car_service_options': json.dumps(car_service_options),
    }
    return render(request, 'service_chatbot.html', context)

# NEW VIEW FOR LAUNCH REGISTRATION
def register_for_launch(request, pk):
    launch = get_object_or_404(UpcomingLaunch, pk=pk)
    if request.method == 'POST':
        form = LaunchRegistrationForm(request.POST)
        if form.is_valid():
            # Check for duplicate registration before saving
            if LaunchRegistration.objects.filter(launch=launch, email=form.cleaned_data['email']).exists():
                messages.warning(request, "You have already registered for this launch with this email.")
            else:
                registration = form.save(commit=False)
                registration.launch = launch
                registration.save()
                messages.success(request, f"Thank you for registering for the {launch.car_name} launch!")
                return redirect('hub:demo') # Redirect to home or a confirmation page
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = LaunchRegistrationForm(initial={'launch': launch.pk}) # Pre-fill launch ID

    context = {
        'form': form,
        'launch': launch,
    }
    return render(request, 'register_for_launch.html', context)

# About Us View
def about_us(request):
    """
    Renders the About Us page.
    """
    return render(request, 'about_us.html')

from .models import TestDriveBooking, Feedback, Complaint

@csrf_exempt
def book_test_drive_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        car_id = data.get('car_id')
        preferred_date = data.get('preferred_date')
        preferred_time = data.get('preferred_time')

        try:
            car = Car.objects.get(id=car_id)
            TestDriveBooking.objects.create(
                user=request.user,
                car=car,
                preferred_date=preferred_date,
                preferred_time=preferred_time
            )
            return JsonResponse({"success": True, "message": "Test drive booked successfully!"})
        except Car.DoesNotExist:
            return JsonResponse({"success": False, "message": "Selected car does not exist."})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@csrf_exempt
def submit_complaint_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        subject = data.get('subject')
        description = data.get('description')

        try:
            Complaint.objects.create(
                user=request.user,
                subject=subject,
                description=description
            )
            return JsonResponse({"success": True, "message": "Complaint submitted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@csrf_exempt
def submit_feedback_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        rating = data.get('rating')
        comments = data.get('comments')

        try:
            Feedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                rating=rating,
                comments=comments
            )
            return JsonResponse({"success": True, "message": "Thank you for your feedback!"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"success": False, "message": "Invalid request method"})

@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_complaints.html', {'complaints': complaints})

@login_required
def my_test_drives(request):
    test_drives = TestDriveBooking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_test_drives.html', {'test_drives': test_drives})

@login_required
def cancel_test_drive(request, pk):
    test_drive = get_object_or_404(TestDriveBooking, pk=pk, user=request.user)
    
    if test_drive.status == 'Pending':
        test_drive.status = 'Cancelled'
        test_drive.save()
        messages.success(request, 'Your test drive booking has been cancelled.')
    else:
        messages.error(request, 'You can only cancel pending test drive bookings.')
    
    return redirect('hub:my_test_drives')

@login_required
def my_feedback(request):
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_feedback.html', {'feedbacks': feedbacks})