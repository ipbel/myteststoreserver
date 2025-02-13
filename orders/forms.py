from django import forms

from orders.models import Order


class OrderForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ivan'}),
    )
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ivanov'}),)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.ru'}),)
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Беларусь, Минск, ул. Победы, дом 4'}),)

    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'address')
