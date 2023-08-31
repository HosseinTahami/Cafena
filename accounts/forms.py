# django imports
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

# inner modules imports
from .models import Personnel
from orders.models import OrderItem

import re


class PersonnelCreationForm(UserCreationForm):
    class Meta:
        model = Personnel
        fields = ["full_name", "email", "phone_number", "image"]


class PersonnelChangeForm(UserChangeForm):
    class Meta:
        model = Personnel
        fields = ["full_name", "email", "phone_number", "image"]


class UserCustomerLoginForm(forms.Form):
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Phone Number",
                "label": "Phone Number",
            }
        )
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if not re.match(r"09(1[0-9]|3[1-9]|2[1-9])[0-9]{7}", phone_number):
            raise forms.ValidationError("Phone number is not valid!")
        return phone_number


class OTPForm(forms.Form):
    digit1 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(
            attrs={
                "class": "m-3 text-center form-control rounded",
                "type": "text",
                "id": "fourth",
                "maxlength": "1",
            }
        ),
    )
    digit2 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(
            attrs={
                "class": "m-3 text-center form-control rounded",
                "type": "text",
                "id": "fourth",
                "maxlength": "1",
            }
        ),
    )
    digit3 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(
            attrs={
                "class": "m-3 text-center form-control rounded",
                "type": "text",
                "id": "fourth",
                "maxlength": "1",
            }
        ),
    )
    digit4 = forms.CharField(
        max_length=1,
        widget=forms.TextInput(
            attrs={
                "class": "m-3 text-center form-control rounded",
                "type": "text",
                "id": "fourth",
                "maxlength": "1",
            }
        ),
    )


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        exclude = ["order", "price"]
