from django import forms

from django.core.exceptions import ValidationError

from shop_app.error_messages import WRONG_QUANTITY_COUNT


class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField()
    update = forms.BooleanField(required=False,
                                initial=False,
                                widget=forms.HiddenInput)

    def clean_quantity(self):
        data = self.cleaned_data['quantity']

        if data < 1:
            raise ValidationError(WRONG_QUANTITY_COUNT)

        return data
