# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AddCarForm, AddJobForm
from hub.models import Car, JobVacancy, PreBooking # Ensure all models are imported
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages # Import Django's messages framework

@login_required
@never_cache # Ensures the view is never cached by browsers
@staff_member_required # Ensures only staff users can access this view
def admin_dashboard(request):
    """
    Renders the admin dashboard with summary counts.
    """
    # Fetch counts for display on the dashboard cards
    total_cars_count = Car.objects.count()
    active_jobs_count = JobVacancy.objects.filter(is_active=True).count()
    # You might want to filter pre-bookings based on specific statuses for a dashboard overview
    pending_prebookings_count = PreBooking.objects.filter(status='Pending').count() 
    
    context = {
        'total_cars_count': total_cars_count,
        'active_jobs_count': active_jobs_count,
        'pending_prebookings_count': pending_prebookings_count,
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
            messages.success(request, 'Car added successfully!') # Success message
            return redirect('admin_panel:car_list') # Redirect to the car list after successful addition
        else:
            messages.error(request, 'Please correct the errors below.') # Error message for invalid form
    else:
        form = AddCarForm() # Empty form for GET request
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
            messages.success(request, 'Job vacancy posted successfully!') # Success message
            return redirect('admin_panel:job_list') # Redirect to the job list
        else:
            messages.error(request, 'Please correct the errors below.') # Error message
    else:
        form = AddJobForm() # Empty form
    return render(request, 'admin_panel/add_job.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def car_list(request):
    """
    Displays a list of all cars in the inventory.
    """
    cars = Car.objects.all().order_by('-created_at') # Order by creation date, newest first
    return render(request, 'admin_panel/car_list.html', {'cars': cars})

@login_required
@never_cache
@staff_member_required
def job_list(request):
    """
    Displays a list of all job vacancies.
    """
    jobs = JobVacancy.objects.all().order_by('-posted_at') # Order by posted date, newest first
    return render(request, 'admin_panel/job_list.html', {'jobs': jobs})

@login_required
@never_cache
@staff_member_required
def view_prebookings(request):
    """
    Displays a list of all pre-bookings.
    """
    bookings = PreBooking.objects.all().order_by('-booking_date') # Order by booking date, newest first
    return render(request, 'admin_panel/view_prebookings.html', {'bookings': bookings})

# You might add views for editing/deleting cars, jobs, or managing pre-bookings here later.
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
    return render(request, 'admin_panel/add_job.html', {'form': form, 'editing': True}) # Use add_job template, pass 'editing' context

@login_required
@never_cache
@staff_member_required
def delete_job(request, pk):
    job = get_object_or_404(JobVacancy, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job vacancy deleted successfully!')
        return redirect('admin_panel:job_list')
    # For a confirmation page before deletion, you might render a specific template:
    return render(request, 'admin_panel/confirm_delete_job.html', {'job': job})