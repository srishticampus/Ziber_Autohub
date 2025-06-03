# hub/views.py
import os
import joblib
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile
from .models import (
    Car, Cart, CartItem, Order, OrderItem, 
    ServiceBooking, JobVacancy, JobApplication, PreBooking
)
from .forms import ( ServiceBookingForm,
    JobApplicationForm, JobVacancyForm, CheckoutForm,CarDetailsForm, PreBookingForm, UsedCarFilterForm
)
from datetime import timedelta, date

@login_required
def index(request):
    new_cars = Car.objects.filter(is_new=True).order_by('-created_at')[:3]
    old_cars = Car.objects.filter(is_new=False).order_by('-created_at')[:3]
    return render(request, 'index.html',{'new_cars': new_cars, 'old_cars': old_cars})

def demo(request):
    return render(request, 'demo.html')

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
        if not age:
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
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, "You have been successfully logged in.")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')

def logout_user(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

@login_required
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
        cars = cars.filter(price__gte=min_price)
    
    if max_price:
        cars = cars.filter(price__lte=max_price)
    
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
            min_price = float(min_price)
            cars = cars.filter(price__gte=min_price)
        except ValueError:
            pass # Handle invalid input gracefully

    if max_price:
        try:
            max_price = float(max_price)
            cars = cars.filter(price__lte=max_price)
        except ValueError:
            pass # Handle invalid input gracefully

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

@login_required
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
        cars = cars.filter(price__gte=min_price)
    
    if max_price:
        cars = cars.filter(price__lte=max_price)

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
    return render(request, 'car_detail.html', {'car': car})

@login_required
def add_to_cart(request, pk):
    car = get_object_or_404(Car, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        car=car,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < car.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {car} to your cart.")
        else:
            messages.error(request, f"Only {car.stock} available in stock.")
    else:
        messages.success(request, f"Added {car} to your cart.")
    
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    total_price = cart.total_price
    return render(request, 'cart.html', {'cart_items': cart_items,'total_price': total_price})

@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        elif quantity > cart_item.car.stock:
            messages.error(request, f"Only {cart_item.car.stock} available in stock.")
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price,
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data.get('billing_address', ''),
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email']
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    car=item.car,
                    quantity=item.quantity,
                    price=item.car.price
                )
                item.car.stock -= item.quantity
                item.car.save()

            cart.items.all().delete()
            messages.success(request, "Order placed successfully!")
            return redirect('payment_success')
    else:
        form = CheckoutForm(user=request.user) # Pass user to pre-fill email/phone

    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': cart.total_price
    })

@login_required
def buy_now(request, pk):
    car = get_object_or_404(Car, pk=pk)
    # If the car is new, redirect to pre-booking
    if car.is_new:
        return redirect('pre_book_car', car_id=pk)

    # Otherwise, add to cart for immediate purchase flow
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, car=car, defaults={'quantity': 1})
    if not created:
        if cart_item.quantity < car.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {car} to your cart.")
        else:
            messages.error(request, f"Only {car.stock} available in stock.")
    else:
        messages.success(request, f"Added {car} to your cart for purchase.")
    
    return redirect('checkout') # Redirect to checkout directly for "Buy Now"

@login_required
def process_order(request):
    if request.method == 'POST':
        buy_now = request.session.get('buy_now')
        if not buy_now:
            return redirect('car_list')

        car = get_object_or_404(Car, id=buy_now['car_id'])
        order = Order.objects.create(
            car=car,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            quantity=buy_now['quantity'],
            total_price=car.price * buy_now['quantity'],
            user=request.user
        )
        
        del request.session['buy_now']
        return redirect('payment_success')
    return redirect('car_list')

@login_required
def payment(request):
    return render(request, 'payment.html')

@login_required
def payment_success(request):
    return render(request, 'payment_success.html')

@login_required
def book_service(request):
    if request.method == 'POST':
        form = ServiceBookingForm(request.POST, request.FILES)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            
            existing = ServiceBooking.objects.filter(
                service_date=booking.service_date,
                status__in=['Pending', 'Approved']
            ).count()
            
            if existing >= 6:
                messages.error(request, 'All slots are booked for this date.')
            else:
                booking.save()
                messages.success(request, 'Service booked successfully!')
                return redirect('my_bookings')
    else:
        form = ServiceBookingForm()
    
    return render(request, 'service-booking.html', {'form': form})

@login_required
def my_bookings(request):
    bookings = ServiceBooking.objects.filter(user=request.user).order_by('-service_date')
    return render(request, 'my_bookings.html', {'bookings': bookings})

@login_required
def job_list(request):
    jobs = JobVacancy.objects.filter(is_active=True).order_by('-posted_at')
    return render(request, 'job_list.html', {'jobs': jobs})

@login_required
def apply_job(request, pk):
    job = get_object_or_404(JobVacancy, pk=pk, is_active=True)
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('job_list')
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job_list')
    else:
        form = JobApplicationForm()
    
    return render(request, 'apply_job.html', {'form': form, 'job': job})

@login_required
def create_job_vacancy(request):
    if not request.user.is_staff:
        # Instead of PermissionDenied, redirect with a message
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')
    
    if request.method == 'POST':
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy created!')
            return redirect('job_list')
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
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
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

# StaffRequiredMixin definition
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
            car_age = 2025 - data['year']  # no_year
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
        return redirect('my_prebookings')

    if request.method == 'POST':
        form = PreBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.car = car
            # delivery_date is now handled in the model's save method, but can be explicitly set here if needed
            # booking.delivery_date = date.today() + timedelta(days=60) 
            booking.save()
            messages.success(request, f'Successfully pre-booked {car.brand} {car.model}!')
            return redirect('my_prebookings')
    else:
        form = PreBookingForm()

    return render(request, 'prebook_car.html', {'form': form, 'car': car})

@login_required
def my_prebookings(request):
    bookings = PreBooking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'my_prebookings.html', {'bookings': bookings})