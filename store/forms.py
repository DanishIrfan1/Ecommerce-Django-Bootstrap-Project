from django import forms
from .models import Product, ReviewRating

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['product_name', 'slug', 'description', 'price', 'image', 'stock', 'is_available', 'category']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']