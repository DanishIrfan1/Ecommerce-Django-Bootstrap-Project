from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            # if request.user.is_authenticated: # check if the user is authenticated or not
            #     cart_items = CartItem.objects.filter(user=request.user) # if user is authenticated, then get the cart items with the user
            # else:
            cart = Cart.objects.filter(cart_id=_cart_id(request)) # if user is not authenticated, then get the cart with the cart_id
            cart_items = CartItem.objects.all().filter(cart=cart[:1]) # get the cart items with the cart
            for cart_item in cart_items: # loop through the cart items
                cart_count += cart_item.quantity # add the quantity of each cart item to the cart_count
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count) # return the cart_count as a dictionary