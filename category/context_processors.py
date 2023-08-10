from .models import Category

def menu_links(request): # This function will return a dictionary of links to be used in the all template files
    links = Category.objects.all() # Get all the categories
    return dict(links=links) # Return the dictionary