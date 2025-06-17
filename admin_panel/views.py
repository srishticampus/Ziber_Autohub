# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from hub.models import Car, JobVacancy, PreBooking, Accessory
from .models import UpcomingLaunch
from .forms import AddCarForm, AddJobForm, AddAccessoryForm, AddUpcomingLaunchForm

@login_required
@never_cache 
@staff_member_required 
def admin_dashboard(request):
    """
    Renders the admin dashboard with summary counts.
    """
    total_cars_count = Car.objects.count()
    active_jobs_count = JobVacancy.objects.filter(is_active=True).count()
    pending_prebookings_count = PreBooking.objects.filter(status='Booked').count() 
    total_accessories_count = Accessory.objects.count()
    total_upcoming_launches_count = UpcomingLaunch.objects.count() # Get count for upcoming launches
    
    context = {
        'total_cars_count': total_cars_count,
        'active_jobs_count': active_jobs_count,
        'pending_prebookings_count': pending_prebookings_count,
        'total_accessories_count': total_accessories_count,
        'total_upcoming_launches_count': total_upcoming_launches_count, # Pass count to context
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@never_cache
@staff_member_required
def add_car(request):
    """
    Handles adding a new car to the inventory.
    """
    if request.method == 'POST':
        form = AddCarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car added successfully!') 
            return redirect('admin_panel:car_list') 
        else:
            messages.error(request, 'Please correct the errors below.') 
    else:
        form = AddCarForm() 
    return render(request, 'admin_panel/add_car.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def add_job(request):
    """
    Handles posting a new job vacancy.
    """
    if request.method == 'POST':
        form = AddJobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy posted successfully!') 
            return redirect('admin_panel:job_list') 
        else:
            messages.error(request, 'Please correct the errors below.') 
    else:
        form = AddJobForm() 
    return render(request, 'admin_panel/add_job.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def car_list(request):
    """
    Displays a list of all cars in the inventory.
    """
    cars = Car.objects.all().order_by('-created_at') 
    return render(request, 'admin_panel/car_list.html', {'cars': cars})

# Edit Car View
@login_required
@never_cache
@staff_member_required
def edit_car(request, pk):
    """
    Handles editing an existing car in the inventory.
    """
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        form = AddCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, 'Car updated successfully!')
            return redirect('admin_panel:car_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddCarForm(instance=car)
    # Pass 'editing=True' for the edit view
    return render(request, 'admin_panel/add_car.html', {'form': form, 'editing': True})

# Delete Car View
@login_required
@never_cache
@staff_member_required
def delete_car(request, pk):
    """
    Handles deleting a car from the inventory.
    """
    car = get_object_or_404(Car, pk=pk)
    if request.method == 'POST':
        car.delete()
        messages.success(request, 'Car deleted successfully!')
        return redirect('admin_panel:car_list')
    # Render a confirmation page for GET request
    return render(request, 'admin_panel/confirm_delete_car.html', {'car': car})

@login_required
@never_cache
@staff_member_required
def job_list(request):
    """
    Displays a list of all job vacancies.
    """
    jobs = JobVacancy.objects.all().order_by('-posted_at') 
    return render(request, 'admin_panel/job_list.html', {'jobs': jobs})

@login_required
@never_cache
@staff_member_required
def job_detail(request, pk): 
    """
    Displays the detailed view of a single job vacancy.
    """
    job = get_object_or_404(JobVacancy, pk=pk)
    return render(request, 'admin_panel/job_detail.html', {'job': job})

@login_required
@never_cache
@staff_member_required
def view_prebookings(request):
    """
    Displays a list of all pre-bookings.
    """
    bookings = PreBooking.objects.all().order_by('-booking_date') 
    return render(request, 'admin_panel/view_prebookings.html', {'bookings': bookings})

@login_required
@never_cache
@staff_member_required
def mark_prebooking_delivered(request, pk): 
    """
    Marks a pre-booking as 'Delivered' and decrements the car's stock.
    """
    booking = get_object_or_404(PreBooking, pk=pk)

    if request.method == 'POST':
        if booking.status != 'Delivered': 
            try:
                with transaction.atomic(): 
                    booking.status = 'Delivered'
                    booking.delivery_date = timezone.now().date() 
                    booking.save()

                    car = booking.car
                    if car.stock > 0:
                        car.stock -= 1
                        car.save()
                        messages.success(request, f"Pre-booking for {car.brand} {car.model} marked as Delivered. Stock updated.")
                    else:
                        messages.warning(request, f"Pre-booking for {car.brand} {car.model} marked as Delivered, but car stock was already 0.")

            except Exception as e:
                messages.error(request, f"Error marking pre-booking as delivered: {e}")
        else:
            messages.info(request, "Pre-booking is already marked as Delivered.")
    else:
        messages.error(request, "Invalid request method for this action.")
    
    return redirect('admin_panel:view_prebookings')

@login_required
@never_cache
@staff_member_required
def edit_job(request, pk):
    job = get_object_or_404(JobVacancy, pk=pk)
    if request.method == 'POST':
        form = AddJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job vacancy updated successfully!')
            return redirect('admin_panel:job_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddJobForm(instance=job)
    return render(request, 'admin_panel/add_job.html', {'form': form, 'editing': True}) 

@login_required
@never_cache
@staff_member_required
def delete_job(request, pk):
    job = get_object_or_404(JobVacancy, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job vacancy deleted successfully!')
        return redirect('admin_panel:job_list')
    return render(request, 'admin_panel/confirm_delete_job.html', {'job': job})

# Accessory Management Views
@login_required
@never_cache
@staff_member_required
def accessory_list(request):
    """
    Displays a list of all accessories in the inventory.
    """
    accessories = Accessory.objects.all().order_by('name')
    return render(request, 'admin_panel/accessory_list.html', {'accessories': accessories})

@login_required
@never_cache
@staff_member_required
def add_accessory(request):
    """
    Handles adding a new accessory.
    """
    if request.method == 'POST':
        form = AddAccessoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory added successfully!')
            return redirect('admin_panel:accessory_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAccessoryForm()
    return render(request, 'admin_panel/add_accessory.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def edit_accessory(request, pk):
    """
    Handles editing an existing accessory.
    """
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        form = AddAccessoryForm(request.POST, request.FILES, instance=accessory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Accessory updated successfully!')
            return redirect('admin_panel:accessory_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddAccessoryForm(instance=accessory)
    return render(request, 'admin_panel/add_accessory.html', {'form': form, 'editing': True})

@login_required
@never_cache
@staff_member_required
def delete_accessory(request, pk):
    """
    Handles deleting an accessory.
    """
    accessory = get_object_or_404(Accessory, pk=pk)
    if request.method == 'POST':
        accessory.delete()
        messages.success(request, 'Accessory deleted successfully!')
        return redirect('admin_panel:accessory_list')
    return render(request, 'admin_panel/confirm_delete_accessory.html', {'accessory': accessory})


# Upcoming Launch Management Views
@login_required
@never_cache
@staff_member_required
def upcoming_launch_list(request):
    """
    Displays a list of all upcoming car launches.
    """
    launches = UpcomingLaunch.objects.all().order_by('launch_date', 'launch_time_start')
    return render(request, 'admin_panel/upcoming_launch_list.html', {'launches': launches})

@login_required
@never_cache
@staff_member_required
def add_upcoming_launch(request):
    """
    Handles adding a new upcoming car launch.
    """
    if request.method == 'POST':
        form = AddUpcomingLaunchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Upcoming launch added successfully!')
            return redirect('admin_panel:upcoming_launch_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddUpcomingLaunchForm()
    return render(request, 'admin_panel/add_upcoming_launch.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def edit_upcoming_launch(request, pk):
    """
    Handles editing an existing upcoming car launch.
    """
    launch = get_object_or_404(UpcomingLaunch, pk=pk)
    if request.method == 'POST':
        form = AddUpcomingLaunchForm(request.POST, instance=launch)
        if form.is_valid():
            form.save()
            messages.success(request, 'Upcoming launch updated successfully!')
            return redirect('admin_panel:upcoming_launch_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AddUpcomingLaunchForm(instance=launch)
    return render(request, 'admin_panel/add_upcoming_launch.html', {'form': form, 'editing': True})

@login_required
@never_cache
@staff_member_required
def delete_upcoming_launch(request, pk):
    """
    Handles deleting an upcoming car launch.
    """
    launch = get_object_or_404(UpcomingLaunch, pk=pk)
    if request.method == 'POST':
        launch.delete()
        messages.success(request, 'Upcoming launch deleted successfully!')
        return redirect('admin_panel:upcoming_launch_list')
    return render(request, 'admin_panel/confirm_delete_upcoming_launch.html', {'launch': launch})

