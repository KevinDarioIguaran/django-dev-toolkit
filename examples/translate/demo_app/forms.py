from django import forms

from .models import Product
from django_dev_toolkit.validators import validate_images


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-2 block w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200',
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'mt-2 block w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'mt-2 block w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-900 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'mt-2 block w-full text-slate-900',
            }),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        validate_images(photo)
        return photo
