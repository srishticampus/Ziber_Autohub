#admin_panel/forms.py
from django import forms
from hub.models import Car, JobVacancy, Accessory
from django.contrib.auth.models import User
import re 
from admin_panel.models import UpcomingLaunch 
class AddCarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = [
            'brand', 'name', 'model', 'price', 'fuel_type', 'year',
            'is_new', 'image', 'description', 'stock',
            'kms_driven', 'owner' # 'owner' field refers to previous owners count
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply Bootstrap classes to all applicable fields
        for field_name, field in self.fields.items():
            if field_name == 'is_new':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name == 'image':
                field.widget.attrs.update({'class': 'form-control'}) # file input also gets form-control
            elif isinstance(field.widget, forms.Select):
                # This block will now apply to 'fuel_type' and 'brand' if they are Select widgets
                field.widget.attrs.update({'class': 'form-select'})
            elif not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                # This will apply 'form-control' to text, number, textarea, AND 'owner' field
                field.widget.attrs.update({'class': 'form-control'})

        # Conditional field requirements based on 'is_new'
        is_new_initial_value = True
        if 'is_new' in self.data:
            is_new_initial_value = self.data['is_new'] == 'on'
        elif self.instance.pk:
            is_new_initial_value = self.instance.is_new


        if is_new_initial_value:
            # If it's a new car, these fields are not required
            self.fields['kms_driven'].required = False
            self.fields['owner'].required = False # 'owner' (previous owners) not required for new
            
            # Clear values when hidden/not required
            self.fields['kms_driven'].initial = None
            self.fields['owner'].initial = None
        else:
            # If it's a used car, these fields are required
            self.fields['kms_driven'].required = True
            self.fields['owner'].required = True # 'owner' (previous owners) is required for used

        # Customizing help text for clarification
        self.fields['is_new'].help_text = "Check if this is a brand new car from the dealer."
        self.fields['kms_driven'].help_text = "Required for used cars. Enter the kilometers driven."
        self.fields['owner'].help_text = "Required for used cars. Enter the number of previous owners." # Updated help text


class AddJobForm(forms.ModelForm):
    class Meta:
        model = JobVacancy
        fields = ['title', 'description', 'location', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'is_active':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})

    # Custom validation for the 'title' field
    def clean_title(self):
        title = self.cleaned_data['title']
        # Allow letters, spaces, and hyphens (if needed for titles like "Software-Engineer")
        if not re.fullmatch(r'^[a-zA-Z\s\-]+$', title):
            raise forms.ValidationError("Job title can only contain alphabetic characters, spaces, and hyphens.")
        return title

#  Form for Accessories
class AddAccessoryForm(forms.ModelForm):
    class Meta:
        model = Accessory
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'image':
                field.widget.attrs.update({'class': 'form-control-file'}) # For file inputs
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'}) # For select/dropdown
            else:
                field.widget.attrs.update({'class': 'form-control'}) # For other inputs

#  Form for UpcomingLaunch
class AddUpcomingLaunchForm(forms.ModelForm):
    class Meta:
        model = UpcomingLaunch
        fields = [
            'car_name', 'car_minimal_details', 'car_description', 'image', # Added 'image'
            'launch_date', 'launch_time_start', 'launch_time_end',
            'venue', 'location'
        ]
        widgets = {
            'car_minimal_details': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'car_description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'launch_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'launch_time_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'launch_time_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}), # Widget for image
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply Bootstrap's form-control or form-select where appropriate,
            # excluding widgets already explicitly set (like Textarea, DateInput, TimeInput, FileInput)
            if not isinstance(field.widget, (forms.Textarea, forms.DateInput, forms.TimeInput, forms.FileInput)):
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs.update({'class': 'form-select'})
                else:
                    field.widget.attrs.update({'class': 'form-control'})

