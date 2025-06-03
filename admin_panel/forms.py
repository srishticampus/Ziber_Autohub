from django import forms
from hub.models import Car, JobVacancy

class AddCarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'name', 'model', 'price', 'fuel_type', 'year',
            'is_new', 'image', 'description', 'stock',
            'kms_driven', 'owner'
        ]

class AddJobForm(forms.ModelForm):
    class Meta:
        model = JobVacancy
        fields = ['title', 'description', 'location', 'is_active']
