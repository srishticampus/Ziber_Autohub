# admin_panel/forms.py
from django import forms
from hub.models import Car, JobVacancy
from django.contrib.auth.models import User
import re # Import regex module

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
        
        # We no longer need to populate 'owner' queryset as it's an IntegerField.
        # self.fields['owner'].queryset = User.objects.filter(...) # REMOVE THIS LINE
        # self.fields['owner'].empty_label = "--- Select an owner (if used car) ---" # REMOVE THIS LINE


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