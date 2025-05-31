from django import forms


from django.core.exceptions import ValidationError
from .models import JobApplication, JobVacancy
from .models import ServiceBooking

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = ['car_model', 'service_date', 'description', 'car_image']        
        widgets = {
            'car_model': forms.Select(attrs={'class': 'form-select'}),
            'service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'car_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages = {
            'car_model': {'required': "Please select a car model for the service."},
            'service_date': {'required': "Please provide a preferred date for the service."},
            'description': {'required': "Please provide a description of the service needed."},
            'car_image': {'required': "Please upload an image of your car."},
        }

    def clean_description(self):
        description = self.cleaned_data['description']
        if len(description) < 10:
            raise ValidationError("Description must be at least 10 characters long.")
        return description



class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume']

class JobVacancyForm(forms.ModelForm):
    class Meta:
        model = JobVacancy
        fields = ['title', 'description', 'location']
