from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Service, Booking, Review


class BootstrapFormMixin:
    """Adds Bootstrap's form-control class to every visible field automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.RadioSelect):
                continue
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.RadioSelect)
    city = forms.CharField(max_length=80)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "phone", "city", "avatar",
            "business_name", "bio", "years_experience",
        ]
        widgets = {"bio": forms.Textarea(attrs={"rows": 4})}


class ServiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Service
        fields = [
            "category", "title", "description", "price",
            "duration_minutes", "city", "image", "is_active",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class BookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["scheduled_date", "scheduled_time", "address", "notes"]
        widgets = {
            "scheduled_date": forms.DateInput(attrs={"type": "date"}),
            "scheduled_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ReviewForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
