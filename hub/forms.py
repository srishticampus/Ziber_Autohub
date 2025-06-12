# hub/forms.py
from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, ServiceBooking, JobApplication, JobVacancy, PreBooking,Car,Accessory

class UserRegistrationForm(UserCreationForm):
    age = forms.IntegerField(min_value=0)
    place = forms.CharField(max_length=100)
    contact_number = forms.CharField(max_length=15)
    image = forms.ImageField(required=False)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 
                  'age', 'place', 'contact_number', 'image', 'gender']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                age=self.cleaned_data['age'],
                place=self.cleaned_data['place'],
                contact_number=self.cleaned_data['contact_number'],
                image=self.cleaned_data['image'],
                gender=self.cleaned_data['gender']
            )
        return user

# class ServiceBookingForm(forms.ModelForm):
#     class Meta:
#         model = ServiceBooking
#         fields = ['car_model', 'service_date', 'description', 'car_image']
#         widgets = {
#             'service_date': forms.DateInput(attrs={'type': 'date'}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({'class': 'form-control'})

#     def clean_service_date(self):
#         date = self.cleaned_data.get('service_date')
#         if date and date < timezone.now().date():
#             raise ValidationError("Service date cannot be in the past.")
#         return date

class JobApplicationForm(forms.ModelForm):
    cover_letter = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
        widgets = {
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class JobVacancyForm(forms.ModelForm):
    class Meta:
        model = JobVacancy
        fields = ['title', 'description', 'location', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# --- NEW FORMS FOR CART AND CHECKOUT ---

class AddToCartForm(forms.Form):
    """
    Form for adding items (cars or accessories) to the cart.
    The product ID is passed via the URL, so only quantity is needed here.
    """
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1', # HTML5 min attribute
            'placeholder': 'Quantity'
        })
    )

class CheckoutForm(forms.Form):
    """
    Form for users to input shipping details and select a payment method during checkout.
    """
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    address_line1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'})
    )
    address_line2 = forms.CharField(
        max_length=255,
        required=False, # Optional field
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (Optional)'})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'})
    )
    zip_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zip/Postal Code'})
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'})
    )
    
    PAYMENT_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        # You can add more payment options here later, e.g., 'credit_card'
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )



class CarDetailsForm(forms.Form):
    present_price = forms.FloatField(label="Present Price (in lakhs)")
    kms_driven = forms.IntegerField(label="Kilometers Driven")
    owner = forms.IntegerField(label="Number of Previous Owners")
    year = forms.IntegerField(label="Year of Purchase")
    fuel_type = forms.ChoiceField(choices=[('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('CNG', 'CNG')])
    seller_type = forms.ChoiceField(choices=[('Dealer', 'Dealer'), ('Individual', 'Individual')])
    transmission = forms.ChoiceField(choices=[('Manual', 'Manual'), ('Automatic', 'Automatic')])


class PreBookingForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Your Delivery Address"
    )

    class Meta:
        model = PreBooking
        fields = ['address']

# Added for used car filters
class UsedCarFilterForm(forms.Form):
    q = forms.CharField(max_length=100, required=False, label='Search',
                        widget=forms.TextInput(attrs={'placeholder': 'Search by model, brand...'}))
    year = forms.ChoiceField(choices=[], required=False, label='Year')
    brand = forms.ChoiceField(choices=[], required=False, label='Brand')
    min_price = forms.FloatField(required=False, label='Min Price',
                                 widget=forms.NumberInput(attrs={'placeholder': 'Min Price'}))
    max_price = forms.FloatField(required=False, label='Max Price',
                                 widget=forms.NumberInput(attrs={'placeholder': 'Max Price'}))
    min_kms = forms.IntegerField(required=False, label='Min Kilometers Driven',
                                 widget=forms.NumberInput(attrs={'placeholder': 'Min Kms'}))
    max_kms = forms.IntegerField(required=False, label='Max Kilometers Driven',
                                 widget=forms.NumberInput(attrs={'placeholder': 'Max Kms'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['year'].choices = [('', 'All Years')] + [(str(y), str(y)) for y in Car.objects.filter(is_new=False).values_list('year', flat=True).distinct().order_by('-year')]
        self.fields['brand'].choices = [('', 'All Brands')] + [(b, b) for b in Car.objects.filter(is_new=False).values_list('brand', flat=True).distinct().order_by('brand')]
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class UsedCarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['is_new','stock']

    def save(self, commit=True):
        car = super().save(commit=False)
        car.is_new = False
        if commit:
            car.save()
        return car