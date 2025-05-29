from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    place = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, unique=True)
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])

    def __str__(self):
        return self.user.username



from django.db import models

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
       
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    year = models.PositiveIntegerField()
    is_new = models.BooleanField(default=True)
    image = models.ImageField(upload_to='car_images/')
    description = models.TextField()

    def __str__(self):
        return f"{self.brand} {self.model} ({'New' if self.is_new else 'Used'})"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.car} ({self.quantity})"
    

class Order(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.car.brand} {self.car.model}"
    

class ServiceBooking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car_model = models.CharField(max_length=100)
    service_date = models.DateField()
    description = models.TextField()
    car_image = models.ImageField(upload_to='car_images/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.car_model}"



# Job Vacancy Model
class JobVacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Job Application Model
class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    job = models.ForeignKey(JobVacancy, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"
