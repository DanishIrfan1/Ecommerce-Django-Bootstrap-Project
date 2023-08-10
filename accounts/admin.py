from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = (
        'email', 'first_name', 'last_name', 'username')  # list_display_links is used to make the fields clickable
    readonly_fields = ('last_login', 'date_joined')  # readonly_fields is used to make the fields read-only
    ordering = ('-date_joined',)  # ordering is used to order the users by date joined
    # below three fields are essintial for the custom admin panel
    filter_horizontal = ()  # filter_horizontal is used to display the fields horizontally
    list_filter = ()  # list_filter is used to filter the fields in the admin panel by date joined
    fieldsets = ()  # fieldsets is used to display the fields in the admin panel


admin.site.register(Account, AccountAdmin)
