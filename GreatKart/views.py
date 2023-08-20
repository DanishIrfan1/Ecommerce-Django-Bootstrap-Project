from django.shortcuts import render
from store.models import Product, ReviewRating


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date') # get all the products which are available and order by created_date

    # Get the reviews
    for product in products: # for loop is used to get the reviews of the products
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True) # get the reviews of the product
    context = {
        'products': products,
        'reviews': reviews,
    }

    return render(request, 'home.html',context)
