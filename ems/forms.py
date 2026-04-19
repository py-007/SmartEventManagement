"""
EMS Forms: Registration, Login, Event, Profile
Clean validation and Bootstrap-compatible widgets.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Profile, Event, Registration


# ──────────────────────────────────────────────
# AUTH FORMS
# ──────────────────────────────────────────────

class RegisterForm(UserCreationForm):
    """User registration form with role selection."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': 'Email address'}
    ))
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'First name'}
    ))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Last name'}
    ))
    role = forms.ChoiceField(
        choices=[('attendee', 'Attendee'), ('manager', 'Event Manager')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Update profile role (profile is auto-created by signal)
            user.profile.role = self.cleaned_data['role']
            user.profile.save()
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control', 'placeholder': 'Password'
        })


# ──────────────────────────────────────────────
# EVENT FORM
# ──────────────────────────────────────────────

class EventForm(forms.ModelForm):
    """Event creation/edit form."""
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'}
        ),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'venue',
            'date', 'total_seats', 'status', 'banner', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue address'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'banner': forms.FileInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'tag1, tag2, tag3'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        # Allow editing existing past events; only restrict new events
        if not self.instance.pk and date and date < timezone.now():
            raise forms.ValidationError("Event date must be in the future.")
        return date

    def clean_total_seats(self):
        seats = self.cleaned_data.get('total_seats')
        if self.instance.pk:
            # Cannot reduce seats below current confirmed registrations
            confirmed = self.instance.registrations.filter(status='confirmed').count()
            if seats < confirmed:
                raise forms.ValidationError(
                    f"Cannot reduce seats below {confirmed} (current confirmed registrations)."
                )
        return seats


# ──────────────────────────────────────────────
# PROFILE FORM
# ──────────────────────────────────────────────

class ProfileForm(forms.ModelForm):
    """Profile editing form."""
    first_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    last_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control'}
    ))
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))

    class Meta:
        model = Profile
        fields = ['phone', 'bio', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 XXXXX XXXXX'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
        self._user = user

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self._user:
            self._user.first_name = self.cleaned_data.get('first_name', '')
            self._user.last_name = self.cleaned_data.get('last_name', '')
            self._user.email = self.cleaned_data.get('email', '')
            if commit:
                self._user.save()
        if commit:
            profile.save()
        return profile


# ──────────────────────────────────────────────
# ADMIN: Role Management Form
# ──────────────────────────────────────────────

class UserRoleForm(forms.ModelForm):
    """Admin form to change user roles."""
    class Meta:
        model = Profile
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'})
        }
