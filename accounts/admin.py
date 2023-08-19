from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


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


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="40" style="border-radius:50%;" />'.format(
            object.profile_picture.url))  # format_html is used to format the html code

    thumbnail.short_description = 'Profile Picture'  # short_description is used to display the name of the field in the admin panel
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
