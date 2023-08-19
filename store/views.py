from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from carts.models import CartItem
from orders.models import OrderProduct
from .forms import ReviewForm
from .models import Product, ReviewRating
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib import messages

# Create your views here.

def store(request, category_slug=None):  # category_slug=None is used to make the category_slug optional
    categories = None  # categories is used to store the category_slug
    products = None  # products is used to store the products

    if category_slug != None:  # if category_slug is not None, then the category_slug is stored in categories, iT MEANS THAT IF THE CATEGORY IS SELECTED THEN THE PRODUCTS OF THAT CATEGORY WILL BE DISPLAYED OR FILTERED
        categories = get_object_or_404(Category,
                                       slug=category_slug)  # get_object_or_404() is used to get the object of the Category model with the slug=category_slug
        products = Product.objects.filter(category=categories,
                                          is_available=True)  # products is used to store the products of the category_slug
        paginator = Paginator(products, 6)  # 6 is the number of products per page
        page = request.GET.get('page')  # get the page number
        paged_products = paginator.get_page(page)  # get the products for the page number
        products_count = products.count()
    else:  # if category_slug is None, then all the products are stored in products
        products = Product.objects.all().filter(is_available=True).order_by("id") # Order_by(id) because we remove warning in the console "UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'store.models.Product'> QuerySet."
        paginator = Paginator(products, 6)  # 6 is the number of products per page
        page = request.GET.get('page')  # get the page number
        paged_products = paginator.get_page(page)  # get the products for the page number
        products_count = products.count()

    context = {
        'products': paged_products,  # products is passed as a context
        'products_count': products_count,
    }
    return render(request, 'store\store.html', context)


def product_detail(request, category_slug, product_slug):  # category_slug and product_slug are passed as parameters
    try:
        single_product = Product.objects.get(category__slug=category_slug,
                                             slug=product_slug)  # get the product with the category_slug and product_slug and category__slug, double underscore use because of foreign key and get slug from other model
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
            request),
            product=single_product).exists()  # check if the product is in the cart or not and return True or False

    except Exception as e:
        raise e
    if request.user.is_authenticated: # check if the user is authenticated or not
        try: # check the orderproduct table if the user already owns the product or not, then it allows the user to submit the review
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else: # if the user is not authenticated then orderproduct will be None
        orderproduct = None
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
    }
    return render(request, 'store\product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            products_count = products.count()
    context = {
        'products': products,
        'products_count': products_count,
    }
    return render(request, 'store\store.html',context)

def submit_review(request,product_id):
    url = request.META.get('HTTP_REFERER') # get the last url
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id) # get the review of the user and product
            form = ReviewForm(request.POST, instance=reviews) # instance=reviews is used to update the review, if the review is already submitted
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist: # if the review is not submitted then create a new review
            form = ReviewForm(request.POST) # create a form instance
            if form.is_valid(): # check if the form is valid or not
                data = ReviewRating() # create an object
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR') # get the ip address
                data.product_id = product_id
                data.user_id = request.user.id
                data.save() # save the data
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)