from django.contrib import admin
from .models import Product, Variation, ReviewRating, ProductGallery
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image') # for product gallery to show in admin panel, by using this we intall pip install django-admin-thumbnails package then import admin_thumbnails and use @admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline): # for product gallery to show in admin panel
    model = ProductGallery # model name
    extra = 1 # extra 1 means 1 extra field will be shown
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'created_date', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline] # for product gallery to show in admin panel

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active')
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)