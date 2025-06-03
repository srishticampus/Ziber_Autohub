# hub/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, date

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField()
    place = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.age < 0:
            raise ValidationError({'age': 'Age cannot be negative.'})

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Car(models.Model):
    BRAND_CHOICES = [
        ('ZIBER', 'ZIBER'),
        ('Toyota', 'Toyota'),
        ('Hyundai', 'Hyundai'),
        ('Honda', 'Honda'),
        ('Suzuki', 'Suzuki'),
    ]

    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars', null=True)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES)
    name = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    year = models.PositiveIntegerField()
    is_new = models.BooleanField(default=True)
    image = models.ImageField(upload_to='car_images/')
    description = models.TextField()
    stock = models.PositiveIntegerField(default=1)
    # Added for used cars
    kms_driven = models.PositiveIntegerField(blank=True, null=True) 
    owner = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'brand']

    def __str__(self):
        return f"{self.year} {self.brand} {self.model}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return self.items.count()

    def __str__(self):
        return f"Cart #{self.id} for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.car.price * self.quantity

    def clean(self):
        if self.quantity > self.car.stock:
            raise ValidationError(f"Only {self.car.stock} available in stock.")

    def __str__(self):
        return f"{self.quantity}x {self.car} in Cart #{self.cart.id}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.car} in Order #{self.order.id}"

class ServiceBooking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_bookings')
    car_model = models.CharField(max_length=100)
    service_date = models.DateField()
    description = models.TextField()
    car_image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-service_date']
        verbose_name_plural = 'Service Bookings'

    def clean(self):
        if self.service_date < timezone.now().date():
            raise ValidationError({'service_date': 'Service date cannot be in the past.'})

    def __str__(self):
        return f"Service for {self.car_model} on {self.service_date}"

class JobVacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-posted_at']
        verbose_name_plural = 'Job Vacancies'

    def __str__(self):
        return f"{self.title} at {self.location}"

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'applicant']

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.username}"
    
class PreBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    booking_date = models.DateField(auto_now_add=True)
    # Make delivery_date nullable in the database
    delivery_date = models.DateField(null=True, blank=True) # <--- ADDED null=True, blank=True
    address = models.TextField()
    payment_status = models.CharField(max_length=20, default="Pending")
    status = models.CharField(max_length=20, default="Booked")

    def save(self, *args, **kwargs):
        # Set booking_date if it's a new instance and not already set
        # (auto_now_add handles this usually, but good for robustness if you manipulate objects)
        if not self.booking_date:
            self.booking_date = date.today() # Or timezone.now().date()

        # Calculate delivery_date ONLY if it's a new instance AND it hasn't been set yet
        # or if you specifically want to recalculate it if it's None.
        # The 'if not self.pk' ensures it's only set on creation.
        if not self.pk and self.delivery_date is None: # Use self.pk for new instance check
            self.delivery_date = self.booking_date + timedelta(days=60)

        # Ensure that if booking_date is already set by auto_now_add or manually,
        # it's used for the delivery_date calculation.
        # The error was primarily because `delivery_date` was `None` initially.
        # By setting `null=True, blank=True`, we allow it to be None in the database.
        # The `if not self.pk` block handles the initial calculation.
        # For existing objects, if delivery_date needs recalculation,
        # you'd need additional logic.

        # Update status based on delivery_date
        # This check should happen *after* delivery_date is guaranteed to have a value
        # and it should apply to both new and existing objects when they are saved.
        # Ensure self.delivery_date is not None before comparison.
        if self.delivery_date and date.today() >= self.delivery_date:
            self.status = "Delivered"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pre-Booking for {self.car.brand} {self.car.model} by {self.user.username}"