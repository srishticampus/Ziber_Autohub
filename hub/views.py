#hub/views.py
import os
import joblib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import UserProfile
from .models import (
    Car, Cart, CartItem, Order, OrderItem, 
    ServiceBooking, JobVacancy, JobApplication
)
from .forms import (
    UserRegistrationForm, ServiceBookingForm,
    JobApplicationForm, JobVacancyForm, CheckoutForm,CarDetailsForm
)

def index(request):
    return render(request, 'index.html')

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

        if User.objects.filter(username=username).exists():
            errors['username'] = "Username already exists!"

        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = "Invalid email format!"

        if User.objects.filter(email=email).exists():
            errors['email'] = "Email already exists!"

        if UserProfile.objects.filter(contact_number=contact_number).exists():
            errors['contact_number'] = "This contact number is already registered!"

        if password != confirm_password:
            errors['password'] = "Passwords do not match!"

        if errors:
            return render(request, 'register.html', {'errors': errors})

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
    cars = Car.objects.filter(
        Q(name__icontains=query) | 
        Q(brand__icontains=query) |
        Q(model__icontains=query)
    ).order_by('-year', 'brand')
    return render(request, 'car_list.html', {'cars': cars, 'query': query})

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
    # cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'cart.html')

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
    
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('view_cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=cart.total_price,
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data.get('billing_address', ''),
                phone=form.cleaned_data['phone'],
                email=form.cleaned_data['email']
            )
            
            for item in cart.items.all():
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
        form = CheckoutForm(user=request.user)
    
    return render(request, 'checkout.html', {
        'form': form,
        'cart': cart
    })

@login_required
def buy_now(request, pk):
    car = get_object_or_404(Car, pk=pk)
    request.session['buy_now'] = {
        'car_id': car.id,
        'quantity': 1
    }
    return render(request, 'checkout.html', {'car': car})

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
        return redirect('home')
    
    if request.method == 'POST':
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy created!')
            return redirect('job_list')
    else:
        form = JobVacancyForm()
    
    return render(request, 'job_list.html', {'form': form})

def news(request):
    return render(request, 'news_details.html')

def products(request):
    return render(request, 'p_details.html')

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
model = joblib.load(model_path)

def predict_price(request):
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
