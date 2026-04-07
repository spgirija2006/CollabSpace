from django import forms
from .models import Project, Application


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'description', 'duration',
            'is_tech', 'is_non_tech',
            'is_paid', 'is_unpaid',
            'is_part_time', 'is_full_time',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['application_message', 'resume']
        widgets = {
            'application_message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell the project creator why you are a good fit...'
            }),
        }