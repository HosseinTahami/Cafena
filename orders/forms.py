# django imports
from django import forms
from .models import Table


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=0,
        max_value=9,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=1,
    )


class CustomerForm(forms.Form):
    TABLE_CHOICES = [
        (
            table.table_number,
            "Name: "
            + str(table.table_number)
            + " / "
            + "Number: "
            + str(table.table_number),
        )
        for table in Table.objects.all()
    ]
    phone_number = forms.CharField(max_length=11, widget=forms.TextInput)
    table_number = forms.ChoiceField(choices=TABLE_CHOICES)
