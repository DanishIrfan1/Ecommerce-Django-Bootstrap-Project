from django.db import models
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:  # Metaclass is used to change the name of the model in the admin panel from categorys to categories
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):  # This method is used to get the url of the category
        return reverse('products_by_category', args=[
            self.slug])  # products_by_category is the name of the url pattern in store\urls.py, reverse function get slugs from self.slug and pass it to the url pattern

    def __str__(
            self):  # This method is used to display the name of the category in the admin panel instead of category object
        return self.category_name
