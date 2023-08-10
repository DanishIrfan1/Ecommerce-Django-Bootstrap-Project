from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class MyAccountManager(BaseUserManager):  # BaseUserManager is used to create a custom user model in Django
    def create_user(self, first_name, last_name, username, email,
                    password=None):  # This method is used to create a user
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),  # normalize_email is used to convert the email to lowercase
            username=username,
            first_name=first_name,
            last_name=last_name,
        )  # self.model is used to create a new user model object

        user.set_password(password)  # set_password is used to set the password of the user
        user.save(using=self._db)  # using=self._db is used to save the user in the database
        return user

    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),  # normalize_email is used to convert the email to lowercase
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True  # is_admin is used to check if the user is an admin or not
        user.is_staff = True  # is_staff is used to check if the user is a staff or not
        user.is_active = True  # is_active is used to check if the user is active or not
        user.is_superuser = True  # is_superuser is used to check if the user is a superuser or not
        user.save(using=self._db)  # using=self._db is used to save the user in the database
        return user


class Account(AbstractBaseUser):  # AbstractBaseUser is used to create a custom user model in Django
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50,
                                unique=True)  # unique=True is used to make sure that the username is unique
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=50)

    # Required fields
    date_joined = models.DateTimeField(auto_now_add=True) # auto_now_add is used to add the date automatically
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)  # is_admin is used to check if the user is an admin or not
    is_staff = models.BooleanField(default=False)  # is_staff is used to check if the user is a staff or not
    is_active = models.BooleanField(default=False)  # is_active is used to check if the user is active or not
    is_superuser = models.BooleanField(default=False)  # is_superuser is used to check if the user is a superuser or not

    USERNAME_FIELD = 'email'  # USERNAME_FIELD is used to define the username field
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']  # REQUIRED_FIELDS is used to define the required fields

    objects = MyAccountManager()  # objects is used to create a new user model object

    def __str__(self):  # This method is used to display the email of the user in the admin panel instead of user object
        return self.email

    def has_perm(self, perm, obj=None):  # This method is used to check if the user has permissions to view the app
        # or not
        return self.is_admin

    def has_module_perms(self,
                         add_label):  # This method is used to check if the user has permissions to view the app or not
        return True
