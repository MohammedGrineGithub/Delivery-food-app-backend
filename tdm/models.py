from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager

class Wilaya(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Location(models.Model):
    address = models.TextField()
    wilaya = models.ForeignKey(Wilaya, on_delete=models.CASCADE)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

class AppImage(models.Model):
    imagePath = models.URLField(default='https://example.com/default-image.jpg')

class CuisingType(models.Model):
    name = models.CharField(max_length=255)

class Rating(models.Model):
    reviewers_count = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
class Customer(AbstractBaseUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255,unique = True)
    phone = models.CharField(max_length=15, unique=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    password = models.CharField(max_length=255)
    photo = models.ForeignKey(AppImage, on_delete=models.SET_NULL, null=True, blank=True)
    has_notification = models.BooleanField(default=False)
    REQUIRED_FIELDS = ['full_name' , 'password']
    USERNAME_FIELD = 'email'
    objects = CustomUserManager()


class RestaurantMenu(models.Model):
    pass 

class Restaurant(models.Model):
    restaurant_name = models.CharField(max_length=255)
    logo = models.ForeignKey(AppImage, related_name='logo', on_delete=models.CASCADE)
    banner_logo = models.ForeignKey(AppImage, related_name='banner_logo', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    cuisine_type = models.ForeignKey(CuisingType, on_delete=models.CASCADE)
    rating = models.OneToOneField(Rating, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    delivery_price = models.IntegerField()
    delivery_duration = models.IntegerField()
    menu = models.OneToOneField(RestaurantMenu, on_delete=models.CASCADE)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    class Meta:
        indexes = [
            models.Index(fields=['restaurant_name']),
        ]

class Category(models.Model):
    name = models.CharField(max_length=255)
    restaurant_menu = models.ForeignKey(RestaurantMenu, on_delete=models.CASCADE)

class Item(models.Model):
    name = models.CharField(max_length=255)
    ingredients = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    photo = models.ForeignKey(AppImage, on_delete=models.SET_NULL, null=True, blank=True)

class DeliveryPerson(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

class Order(models.Model):
    """ STATUS_CHOICES = [
        (0, 'Waiting'),
        (1, 'Prepared'),
        (2, 'Picked Up'),
        (3, 'On Way'),
        (4, 'Delivered'),
        (5, 'Canceled'),
    ] """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.SmallIntegerField(default=0)
    delivery_note = models.TextField(null=True, blank=True)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    note = models.TextField(null=True, blank=True)
    item_quantity = models.PositiveIntegerField()

class Link(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)

class Comment(models.Model):
    comment = models.TextField()
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)

class Notification(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    