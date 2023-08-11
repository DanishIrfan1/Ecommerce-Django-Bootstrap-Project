from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product
from .models import Cart, CartItem


# Create your views here.

def _cart_id(request):  # _cart_id() is used to get the cart_id from the session
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    color = request.POST['color']
    size = request.POST['size']
    
    product = Product.objects.get(id=product_id)  # get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the _cart_id present in the session
        # print("cart already exists")
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        # print("cart created")
    cart.save()  # save the cart in the session
    # print("cart session id: ", cart.cart_id)
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)  # get the cart_item using the product and cart
        cart_item.quantity += 1  # if the cart_item already exists, then increase the quantity by 1
        cart_item.save()
    except CartItem.DoesNotExist:  # if the cart_item does not exist, then create the cart_item
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )  # create the cart_item
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id):  # remove_cart() is used to remove the cart_item from the cart for (-) button
    cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)  # get the product
    cart_item = CartItem.objects.get(product=product, cart=cart)  # get the cart_item using the product and cart
    if cart_item.quantity > 1:  # if the quantity of the cart_item is greater than 1
        cart_item.quantity -= 1  # then decrease the quantity by 1
        cart_item.save()  # save the cart_item
    else:
        cart_item.delete()  # else delete the cart_item
    return redirect('cart')


def remove_cart_item(request,
                     product_id):  # remove_cart_item() is used to remove the cart_item from the cart for (x) button
    cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
    product = get_object_or_404(Product, id=product_id)  # get the product
    cart_item = CartItem.objects.get(product=product, cart=cart)  # get the cart_item using the product and cart
    cart_item.delete()  # delete the cart_item
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:

        cart = Cart.objects.get(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)  # get all the cart_items of a particular cart
        for cart_item in cart_items:  # iterate over the cart_items
            total += (cart_item.product.price * cart_item.quantity)  # calculate the total
            quantity += cart_item.quantity  # calculate the total quantity
        tax = (2 * total) / 100  # calculate the tax
        grand_total = total + tax  # calculate the grand total
    except ObjectDoesNotExist:  # if the cart does not exist, then just ignore
        pass  # just ignore
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)
