from .models import Cart, CartItem
from .views import _cart_id


def counter(request):  # counter() is used to count the number of items in the cart
    cart_count = 0  # cart_count is used to store the number of items in the cart
    if 'admin' in request.path:  # if admin is in the request path, then return an empty dictionary because we don't want to show the cart_count in the admin page
        return {}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))  # get the cart using the cart_id present in the session
            if request.user.is_authenticated: # check if the user is authenticated or not
                cart_items = CartItem.objects.all().filter(user=request.user) # if user is authenticated, then get the cart items with the user
            else:
                cart_items = CartItem.objects.all().filter(cart=cart[:1])  # get the cart_item using the cart object, the cart object is sliced because the cart object is a list
            for cart_item in cart_items:  # loop through the cart items
                cart_count += cart_item.quantity  # add the quantity of each cart item to the cart_count
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)  # return the cart_count as a dictionary
