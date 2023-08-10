from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category


# Create your views here.

def store(request, category_slug=None):  # category_slug=None is used to make the category_slug optional
    categories = None  # categories is used to store the category_slug
    products = None  # products is used to store the products

    if category_slug != None:  # if category_slug is not None, then the category_slug is stored in categories
        categories = get_object_or_404(Category,
                                       slug=category_slug)  # get_object_or_404() is used to get the object of the Category model with the slug=category_slug
        products = Product.objects.filter(category=categories,
                                          is_available=True)  # products is used to store the products of the category_slug
        products_count = products.count()
    else:  # if category_slug is None, then all the products are stored in products
        products = Product.objects.all().filter(is_available=True)
        products_count = products.count()

    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'store\store.html', context)


def product_detail(request, category_slug, product_slug):  # category_slug and product_slug are passed as parameters
    try:
        single_product = Product.objects.get(category__slug=category_slug,
                                             slug=product_slug)  # get the product with the category_slug and product_slug and category__slug, double underscore use because of foreign key and get slug from other model
    except Exception as e:
        raise e
    context = {
        'single_product': single_product,
    }
    return render(request, 'store\product_detail.html', context)
