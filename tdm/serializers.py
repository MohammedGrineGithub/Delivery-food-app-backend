from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserEmailLoginSerializer(serializers.ModelSerializer):
    class Meta :
        model = Customer
        fields = ['email' , 'password']
        def validate( self, data ):
            user = Customer.objects.filter(email=data['email'])
            if user is None :
                return serializers.ValidationError("Email does not exist.")
            else :
                if user['password'] != data['password']:
                    return serializers.ValidationError("Invalid password.")
class UserPhoneLoginSerializer(serializers.ModelSerializer):
    class Meta :
        model = Customer
        fields = ['phone' , 'password']
        def validate( self, data ):
            user = Customer.objects.filter(email=data['phone'])
            if user is None :
                return serializers.ValidationError("phone number does not exist.")
            else :
                if user['password'] != data['password']:
                    return serializers.ValidationError("Invalid password.")
                       
class CustomTokenObtainPairSerializerForEmail(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
class WilayaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = ['name']
class CustomTokenObtainPairSerializerPhoneNumber(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone'] = user.phone
        return token
class RatingSerrializer(serializers.ModelSerializer) :
    class Meta :
        model = Rating
        fields = [ 'rating' , 'reviewers_count' ]
class ImageSerializer(serializers.ModelSerializer) :
    class Meta:
        model = AppImage
        fields = ['id', 'imagePath']
        
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['wilayaId', 'address', 'latitude', 'longitude']

class RestaurantSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()
    banner_logo = ImageSerializer()
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    cuisine_type = serializers.PrimaryKeyRelatedField(queryset=CuisingType.objects.all())
    rating = RatingSerrializer()
    menu = serializers.PrimaryKeyRelatedField(queryset=RestaurantMenu.objects.all())
    class Meta:
        model = Restaurant
        fields = '__all__'

    def create(self, validated_data):
        logo_data = validated_data.pop('logo')
        banner_logo_data = validated_data.pop('banner_logo')
        rating_data = validated_data.pop('rating')
        menu_data = validated_data.pop('menu')
        location_data = validated_data.pop('location')
        cuisine_type_data = validated_data.pop('cuisine_type')
        
        logo = AppImage.objects.create(**logo_data)
        banner_logo = AppImage.objects.create(**banner_logo_data)
        rating = Rating.objects.create(**rating_data)
        menu = RestaurantMenu.objects.create() if menu_data is None else menu_data 
        location = Location.objects.create(**location_data)
        cuisine_type = CuisingType.objects.create(**cuisine_type_data)

        restaurant = Restaurant.objects.create(
            logo=logo,
            banner_logo=banner_logo,
            rating=rating,
            menu=menu,
            location=location,
            cuisine_type=cuisine_type,
            **validated_data
        )        
        return restaurant
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class RestaurantMenuCreationSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    class Meta:
        model = RestaurantMenu
        fields = '__all__'

    def create(self, validated_data):
        categories_data = validated_data.pop('categories')
        restaurant_menu = RestaurantMenu.objects.create(**validated_data)
        for category_data in categories_data:
            items_data = category_data.pop('items', [])
            category = Category.objects.create(menu=restaurant_menu, **category_data)
            for item_data in items_data:
                Item.objects.create(category=category, **item_data)
        return restaurant_menu
    
   
class RestaurantOverViewSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()
    banner_logo = ImageSerializer()
    rating = RatingSerrializer()
    class Meta:
        model = Restaurant
        fields = ['id', 'restaurant_name', 'logo', 'banner_logo', 'rating', 'delivery_price', 'delivery_duration','open_time', 'close_time']
 
class CustomerSerializer(serializers.ModelSerializer):
    photo = ImageSerializer(required=False)
    location = LocationSerializer(required=False)

    class Meta:
        model = Customer
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }

    def validate_email(self, value):
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("The email is already taken.")
        elif not value:
            raise serializers.ValidationError("The email is required.")
        return value

    def create(self, validated_data):
        photo_data = validated_data.pop('photo', None)
        location_data = validated_data.pop('location', None)
        photo = AppImage.objects.create(**photo_data) if photo_data else None
        location = Location.objects.create(**location_data) if location_data else None
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError("Password is required.")
        customer = Customer.objects.create_user(
            photo=photo,
            location=location,
            password=password,
            **validated_data
        )
        
        return customer 
class CuisinTypeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = CuisingType
        fields = "__all__"
        
        
class ItemSerializer(serializers.ModelSerializer):  
    photo = ImageSerializer()
    class Meta:
        model = Item
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = '__all__'