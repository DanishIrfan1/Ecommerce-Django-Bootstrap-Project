from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from carts.models import CartItem
from .models import Product
from category.models import Category
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


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
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
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