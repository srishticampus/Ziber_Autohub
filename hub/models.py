# hub/models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
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

class Accessory(models.Model):
    CATEGORY_CHOICES = [
        ('Interior', 'Interior'),
        ('Exterior', 'Exterior'),
        ('Performance', 'Performance'),
        ('Electronic', 'Electronic'),
        ('Safety', 'Safety'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='accessory_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    # Optional: If you want to link accessories to specific cars
    # compatible_cars = models.ManyToManyField(Car, blank=True, related_name='accessories') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Accessories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def get_total_price(self):
        """Calculates the total price of all items in the cart."""
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True) # Can be a Car
    accessory = models.ForeignKey(Accessory, on_delete=models.SET_NULL, null=True, blank=True) # Can be an Accessory
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        # Ensures that for a given cart, there's only one entry for a specific car or accessory.
        # This will be enforced more robustly by the clean method.
        # Unique constraints might need careful handling with nullables; custom validation is safer.
        pass

    def clean(self):
        """Custom validation to ensure item is either a car or an accessory, but not both."""
        if self.car and self.accessory:
            raise ValidationError("A cart item cannot be both a car and an accessory.")
        if not self.car and not self.accessory:
            raise ValidationError("A cart item must be either a car or an accessory.")
        
        # Validate quantity for cars (only 1 car per cart item)
        if self.car and self.quantity > 1:
            raise ValidationError("You can only add one car per cart item. Please add cars as separate items if needed.")

    def get_product(self):
        """Returns the associated Car or Accessory object."""
        return self.car if self.car else self.accessory

    def get_item_price(self):
        """Returns the price of the single product (car or accessory)."""
        product = self.get_product()
        return product.price if product else 0

    def get_total_price(self):
        """Returns the total price for this cart item (price * quantity)."""
        return self.get_item_price() * self.quantity

    def __str__(self):
        product = self.get_product()
        if product:
            return f"{self.quantity} x {product.name} in {self.cart.user.username}'s cart"
        return f"Invalid CartItem in {self.cart.user.username}'s cart"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Statuses: Pending, Processing, Completed, Cancelled, Refunded
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    # Shipping details (could be linked to UserProfile or taken from form)
    shipping_address = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Optional: Add delivery date for tracking
    delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def save(self, *args, **kwargs):
        # Calculate total_amount if it's a new order or items have changed (needs manual trigger in view)
        if not self.pk: # For new orders, calculate total_amount before initial save
            super().save(*args, **kwargs) # Save to get an ID for items to link to
            # Calculate total_amount based on associated order items (handled in checkout view)
            # self.total_amount will be updated after order items are created.
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)
    accessory = models.ForeignKey(Accessory, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at time of order

    class Meta:
        # Same validation applies as CartItem
        pass

    def clean(self):
        """Custom validation to ensure item is either a car or an accessory, but not both."""
        if self.car and self.accessory:
            raise ValidationError("An order item cannot be both a car and an accessory.")
        if not self.car and not self.accessory:
            raise ValidationError("An order item must be either a car or an accessory.")
        
        # Validate quantity for cars (only 1 car per order item)
        if self.car and self.quantity > 1:
            raise ValidationError("You can only order one car per order item.")

    def get_product(self):
        """Returns the associated Car or Accessory object."""
        return self.car if self.car else self.accessory

    def get_total_price(self):
        """Returns the total price for this order item (price * quantity)."""
        return self.price * self.quantity

    def __str__(self):
        product = self.get_product()
        if product:
            return f"{self.quantity} x {product.name} for Order {self.order.id}"
        return f"Invalid OrderItem for Order {self.order.id}"



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
    delivery_date = models.DateField(null=True, blank=True)
    address = models.TextField()
    payment_status = models.CharField(max_length=20, default="Pending")
    status = models.CharField(max_length=20, default="Booked")

    def save(self, *args, **kwargs):
        # Set booking_date if it's a new instance and not already set
        if not self.booking_date:
            self.booking_date = date.today()

        # Calculate delivery_date ONLY if it's a new instance AND it hasn't been set yet
        if not self.pk and self.delivery_date is None:
            self.delivery_date = self.booking_date + timedelta(days=60)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pre-Booking for {self.car.brand} {self.car.model} by {self.user.username}"
    

class ServiceBooking(models.Model):
    SERVICE_CHOICES = [
        ('1st', '1st Service'),
        ('2nd', '2nd Service'),
        ('3rd', '3rd Service'),
        ('4th', '4th Service'),
    ]

    STATUS_CHOICES = [
        ('Booked', 'Service Booked'),
        ('Ongoing', 'Service Ongoing'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, null=True)
    service_type = models.CharField(max_length=10, choices=SERVICE_CHOICES, null=True)
    description = models.TextField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')
    booked_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.car} - {self.service_type} ({self.status})"

