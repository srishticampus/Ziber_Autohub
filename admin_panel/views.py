from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AddCarForm, AddJobForm
from hub.models import Car, JobVacancy, PreBooking
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

@login_required
@never_cache
@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

@login_required
@never_cache
@staff_member_required
def add_car(request):
    if request.method == 'POST':
        form = AddCarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:admin_dashboard')
    else:
        form = AddCarForm()
    return render(request, 'admin_panel/add_car.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def add_job(request):
    if request.method == 'POST':
        form = AddJobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_panel:admin_dashboard')
    else:
        form = AddJobForm()
    return render(request, 'admin_panel/add_job.html', {'form': form})

@login_required
@never_cache
@staff_member_required
def car_list(request):
    cars = Car.objects.all()
    return render(request, 'admin_panel/car_list.html', {'cars': cars})

@login_required
@never_cache
@staff_member_required
def job_list(request):
    jobs = JobVacancy.objects.all()
    return render(request, 'admin_panel/job_list.html', {'jobs': jobs})

@login_required
@never_cache
@staff_member_required
def view_prebookings(request):
    bookings = PreBooking.objects.all()
    return render(request, 'admin_panel/view_prebookings.html', {'bookings': bookings})