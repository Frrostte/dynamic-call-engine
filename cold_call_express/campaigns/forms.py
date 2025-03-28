from django import forms
from .models import Campaign, Contact

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'company_details', 'product_service', 'marketing_keywords', 'starting_pitch']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_company_details' }),
            'product_service': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_product_service'}),
            'marketing_keywords': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_marketing_keywords'}),
            'starting_pitch': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_starting_pitch'}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'phone_number', 'email', 'age', 'gender', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='File must be in CSV format with the following columns: name, phone_number, email, age, gender, location'
    )