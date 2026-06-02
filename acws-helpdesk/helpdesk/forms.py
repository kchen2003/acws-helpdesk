from django import forms
from .models import Ticket, TicketUpdate, TeamMember
from django.contrib.auth.forms import AuthenticationForm


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(label='User Name', widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': 'autofocus'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["release_version", "title", "description", "submitter_name", "contact_info"]
        widgets = {
            'release_version': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'submitter_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AssignForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["assigned_to", "status"]

class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = TicketUpdate
        fields = ["note", "status_after"]
