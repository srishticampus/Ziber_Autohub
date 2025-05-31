from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Car, Cart, CartItem, Order, ServiceBooking, JobVacancy, JobApplication

from .models import Car



# Create your views here.
# def home(request):
#     return render(request,'home.html')


def index(request):
    return render(request,'index.html')



def demo(request):
    return render(request,'demo.html')

def news(request):
    return render(request,'news_details.html')


def products(request):
    return render(request,'p_details.html')



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
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_active:
                messages.error(request, "Your account is pending approval by the admin.")
                return redirect('login')

            login(request, user)

            if user.is_superuser:  
                return redirect("admin_panel:admin_dashboard")  
            
            elif UserProfile.objects.filter(user=user).exists():
                messages.success(request, "Login successful! Welcome to your profile.")
                return redirect("car_list")
            
            else:
                messages.success(request, "Login successful!")
                return redirect("home_page")  

        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    return render(request, 'login.html')
  

def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')


from django.db.models import Q

@login_required
def car_list(request):
    query = request.GET.get('q')
    if query:
        cars = Car.objects.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(model__icontains=query)
        )
    else:
        cars = Car.objects.all()
    return render(request, 'car_list.html', {'cars': cars})


@login_required
def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    return render(request, 'car_detail.html', {'car': car})



@login_required
def add_to_cart(request, car_id):
    cart = request.session.get('cart', {})
    car_id_str = str(car_id)
    if car_id_str in cart:
        cart[car_id_str]['quantity'] += 1
    else:
        cart[car_id_str] = {'quantity': 1}
    request.session['cart'] = cart
    return redirect('view_cart') 




@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for car_id_str, item in cart.items():
        try:
            car = Car.objects.get(id=int(car_id_str))
            quantity = item.get('quantity', 1)
            total = car.price * quantity
            total_price += total
            cart_items.append({
                'car': car,
                'quantity': quantity,
                'total': total,
            })
        except Car.DoesNotExist:
            continue  # Skip if car not found

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def buy_now(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    # Store the selected car in the session for checkout
    request.session['buy_now'] = {
        'car_id': car.id,
        'quantity': 1  # Default quantity can be adjusted as needed
    }
    return render(request, 'checkout.html', {'car': car})

@login_required
def process_order(request):
    if request.method == 'POST':
        buy_now = request.session.get('buy_now')
        if not buy_now:
            # Handle the case where there's no item to purchase
            return redirect('car_list')  # Redirect to your car listing page

        car = get_object_or_404(Car, id=buy_now['car_id'])
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')

        # Create and save the order
        order = Order.objects.create(
            car=car,
            name=name,
            email=email,
            address=address,
            quantity=buy_now['quantity'],
            total_price=car.price * buy_now['quantity']
        )

        # Clear the 'buy_now' session data
        del request.session['buy_now']

        return render(request, 'order_confirmation.html', {'order': order})
    else:
        return redirect('car_list')
@login_required
def payment(request):
    # Simulate payment processing
    return render(request, 'payment.html')

@login_required
def payment_success(request):
    # Display payment success message
    return render(request, 'payment_success.html')

@login_required
def checkout(request):
    buy_now = request.session.get('buy_now')
    if not buy_now:
        return redirect('car_list')
    car = get_object_or_404(Car, id=buy_now['car_id'])
    if request.method == 'POST':
        # Process the order here
        return redirect('payment')
    return render(request, 'checkout.html', {'car': car})

@login_required

# @login_required
# def remove_from_cart(request, item_id):
#     item = get_object_or_404(CartItem, id=item_id)
#     item.delete()
#     return redirect('view_cart') 


def book_service(request):
    if request.method == 'POST':
        form = ServiceBookingForm(request.POST, request.FILES)
        if form.is_valid():
            service_date = form.cleaned_data['service_date']
            bookings_count = ServiceBooking.objects.filter(service_date=service_date).count()

            # Limit to 6 bookings per day
            if bookings_count >= 6:
                messages.error(request, 'Booking full for this date. Please select another date.')
                return redirect('book_service')

            # Save the booking with user info
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            messages.success(request, 'Service booked successfully! 🎉 Waiting for admin confirmation.')
            return redirect('home')
    else:
        form = ServiceBookingForm()

    return render(request, 'service-booking.html', {'form': form})


def my_bookings(request):
    bookings = ServiceBooking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})



def job_list(request):
    jobs = JobVacancy.objects.all().order_by('-posted_at')
    return render(request, 'job_list.html', {'jobs': jobs})

def apply_job(request, job_id):
    job = get_object_or_404(JobVacancy, id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()

            messages.success(request, 'Application submitted successfully! 🚀 Waiting for admin review.')
            return redirect('job_list')
    else:
        form = JobApplicationForm()

    return render(request, 'apply_job.html', {'form': form, 'job': job})

# Admin Create Vacancy View

def create_job_vacancy(request):
    if not request.user.is_superuser:
        return redirect('home')  # Only admins allowed

    if request.method == 'POST':
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy posted successfully! 🎯')
            return redirect('job_list')
    else:
        form = JobVacancyForm()
    
    return render(request, 'create_job.html', {'form': form})