#hub/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, ServiceBooking, JobApplication, JobVacancy

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

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = ['car_model', 'service_date', 'description', 'car_image']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_service_date(self):
        date = self.cleaned_data.get('service_date')
        if date and date < timezone.now().date():
            raise ValidationError("Service date cannot be in the past.")
        return date

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

class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    billing_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    phone = forms.CharField(max_length=20)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['email'].initial = user.email
            if hasattr(user, 'profile'):
                self.fields['phone'].initial = user.profile.contact_number
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})