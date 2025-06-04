# admin_panel/urls.py
from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add-car/', views.add_car, name='add_car'),
    path('add-job/', views.add_job, name='add_job'),
    path('prebookings/', views.view_prebookings, name='view_prebookings'),
    path('cars/', views.car_list, name='car_list'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/edit/<int:pk>/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:pk>/', views.delete_job, name='delete_job'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('prebookings/<int:pk>/deliver/', views.mark_prebooking_delivered, name='mark_prebooking_delivered'),
]