from django.db import models

# Create your models here.

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class UserProfile(models.Model):
 user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='User')
    age = models.PositiveIntegerField(verbose_name='Age', help_text='User\'s age')
    place = models.CharField(max_length=100, verbose_name='Place', help_text='User\'s location')
    contact_number = models.CharField(max_length=15, unique=True, verbose_name='Contact Number', help_text='User\'s contact phone number')
    image = models.ImageField(upload_to='user_images/', blank=True, null=True, verbose_name='Profile Image', help_text='Optional profile image')
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def clean(self):
        if self.age is not None and self.age < 0:
            raise ValidationError({'age': 'Age cannot be negative.'})

    def __str__(self):
        return f"Profile of {self.user.username}"



class Car(models.Model):
    BRAND_CHOICES = [
        ('ZIBER', 'ZIBER'),
        ('Toyota', 'Toyota'),
        ('Hyundai', 'Hyundai'),
        ('Honda', 'Honda'),
        ('Suzuki', 'Suzuki'),
        # Add more if needed
    ]

    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]
       
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES, verbose_name='Brand', help_text='Brand of the car')
    name = models.CharField(max_length=50, verbose_name='Name', help_text='Name of the car model')
    model = models.CharField(max_length=100, verbose_name='Model', help_text='Specific model details')

    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price', help_text='Price of the car')
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, verbose_name='Fuel Type', help_text='Type of fuel the car uses')
    year = models.PositiveIntegerField(verbose_name='Year', help_text='Manufacturing year of the car')
    is_new = models.BooleanField(default=True)
    image = models.ImageField(upload_to='car_images/')
    description = models.TextField()

    def __str__(self):
 return f"{self.year} {self.brand} {self.model} ({'New' if self.is_new else 'Used'})"


class Cart(models.Model):
 user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='User')

    def __str__(self):
        return f"Cart of {self.user.username}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
 return f"{self.quantity} x {self.car.brand} {self.car.model}"


class Order(models.Model):
 car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Car')
    name = models.CharField(max_length=255, verbose_name='Customer Name')
    email = models.EmailField(verbose_name='Customer Email')
    address = models.TextField(verbose_name='Delivery Address')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Total Price')
    ordered_at = models.DateTimeField(auto_now_add=True, verbose_name='Ordered At')

    def __str__(self):
 return f"Order #{self.id} for {self.car.brand} {self.car.model}"


class ServiceBooking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

 user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_bookings', verbose_name='User')
    car_model = models.CharField(max_length=100, verbose_name='Car Model for Service', help_text='Specify the model of the car needing service')
    service_date = models.DateField(verbose_name='Service Date', help_text='Preferred date for the service')
    description = models.TextField(verbose_name='Description', help_text='Describe the service needed')
    car_image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
 return f"Service booking for {self.car_model} by {self.user.username} on {self.service_date}"

    def clean(self):
        if self.service_date and self.service_date < timezone.now().date():
            raise ValidationError({'service_date': 'Service date cannot be in the past.'})



# Job Vacancy Model
class JobVacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name='Job Title')
    description = models.TextField(verbose_name='Job Description')
    location = models.CharField(max_length=100, verbose_name='Location')
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
 return f"Job Vacancy: {self.title} at {self.location}"

# Job Application Model
class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

 job = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='applications', verbose_name='Job Vacancy')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications', verbose_name='Applicant')
    resume = models.FileField(upload_to='resumes/', verbose_name='Resume', help_text='Upload your resume')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending', verbose_name='Application Status')

    def __str__(self):
 return f"Application for {self.job.title} by {self.applicant.username}"
