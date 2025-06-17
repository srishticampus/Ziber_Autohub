# admin_panel/urls.py
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Cars
    path('add-car/', views.add_car, name='add_car'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/edit/<int:pk>/', views.edit_car, name='edit_car'),
    path('cars/delete/<int:pk>/', views.delete_car, name='delete_car'),
    
    # Jobs
    path('add-job/', views.add_job, name='add_job'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/edit/<int:pk>/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:pk>/', views.delete_job, name='delete_job'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'), # Detail view for a single job
    
    # Pre-Bookings
    path('prebookings/', views.view_prebookings, name='view_prebookings'),
    path('prebookings/<int:pk>/deliver/', views.mark_prebooking_delivered, name='mark_prebooking_delivered'),

    # Accessories
    path('accessories/', views.accessory_list, name='accessory_list'),
    path('accessories/add/', views.add_accessory, name='add_accessory'),
    path('accessories/edit/<int:pk>/', views.edit_accessory, name='edit_accessory'),
    path('accessories/delete/<int:pk>/', views.delete_accessory, name='delete_accessory'),

    # Upcoming Launches
    path('upcoming-launches/', views.upcoming_launch_list, name='upcoming_launch_list'),
    path('upcoming-launches/add/', views.add_upcoming_launch, name='add_upcoming_launch'),
    path('upcoming-launches/edit/<int:pk>/', views.edit_upcoming_launch, name='edit_upcoming_launch'),
    path('upcoming-launches/delete/<int:pk>/', views.delete_upcoming_launch, name='delete_upcoming_launch'),
]
