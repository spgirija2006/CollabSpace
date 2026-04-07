from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'accept': '.pdf'})
    )
    terms_accepted = forms.BooleanField(
        label="I understand this platform is a mediator only and accept all terms."
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'gender', 'bio', 'resume', 'profile_picture']