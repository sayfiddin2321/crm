from django import forms
from .models import NanoCoinTransaction

class NanoCoinForm(forms.ModelForm):
    class Meta:
        model = NanoCoinTransaction
        fields = ['amount', 'reason']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nechta coin beriladi?'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sababini yozing (masalan: test uchun, bonus va h.k.)'
            }),
        }
        labels = {
            'amount': 'NANOcoin miqdori',
            'reason': 'Sabab',
        }
