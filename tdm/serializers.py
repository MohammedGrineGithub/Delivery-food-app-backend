from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserEmailLoginSerializer(serializers.ModelSerializer):
    class Meta :
        model = Customer
        fields = ['email' , 'password']
        def validate(self, data):
            try:
                user = Customer.objects.get(email=data['email'])
            except Customer.DoesNotExist:
                raise serializers.ValidationError("Email does not exist.")
            
            if not user.check_password(data['password']):
                raise serializers.ValidationError("Invalid password.")
            
            return data
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
                     
class CuisinTypeSerializer(serializers.ModelSerializer) :
    class Meta :
        model = CuisingType
        fields = "__all__"
        
                             
class CustomTokenObtainPairSerializerForEmail(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_active:
            raise serializers.ValidationError("No active account found with the given credentials")

        return data
class WilayaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = ['name']

class WilayaSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = "__all__"
class CustomTokenObtainPairSerializerPhoneNumber(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['phone'] = user.phone
        return token
class RatingSerrializer(serializers.ModelSerializer) :
    class Meta :
        model = Rating
        fields = "__all__"
class ImageSerializer(serializers.ModelSerializer) :
    class Meta:
        model = AppImage
        fields = "__all__"
        
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantMenu
        fields = "__all__"
class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"
class RestaurantDetailsSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()
    banner_logo = ImageSerializer()
    location = LocationSerializer()
    rating = RatingSerrializer()
    class Meta:
        model = Restaurant
        fields = "__all__"      
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
    
   
class RestaurantOverViewSerializer(serializers.ModelSerializer):
    logo = ImageSerializer()
    banner_logo = ImageSerializer()
    rating = RatingSerrializer()
    class Meta:
        model = Restaurant
        fields = ['id', 'restaurant_name', 'logo', 'banner_logo', 'rating', 'delivery_price', 'delivery_duration','opening_time', 'closing_time']
        
        
class CustomerUpdateSerializer(serializers.ModelSerializer):
    photo = ImageSerializer(required=False)
    location = LocationSerializer(required=False)

    class Meta:
        model = Customer
        fields = ["id", "full_name", "phone", "photo", "location", "has_notification"]

    def update(self, instance, validated_data):
        photo_data = validated_data.pop('photo', None)
        location_data = validated_data.pop('location', None)

        if photo_data:
            if instance.photo:
                for attr, value in photo_data.items():
                    setattr(instance.photo, attr, value)
                instance.photo.save()
            else:
                instance.photo = AppImage.objects.create(**photo_data)

        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    
    
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
    def update(self, instance, validated_data):
        photo_data = validated_data.pop('photo', None)
        location_data = validated_data.pop('location', None)

        if photo_data:
            if instance.photo:
                for attr, value in photo_data.items():
                    setattr(instance.photo, attr, value)
                instance.photo.save()
            else:
                instance.photo = AppImage.objects.create(**photo_data)

        if location_data:
            if instance.location:
                for attr, value in location_data.items():
                    setattr(instance.location, attr, value)
                instance.location.save()
            else:
                instance.location = Location.objects.create(**location_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
        
        
class ItemSerializer(serializers.ModelSerializer):  
    photo = ImageSerializer()
    class Meta:
        model = Item
        fields = '__all__'
    def create(self, validated_data):
        photo_data = validated_data.pop('photo', None)
        category_data = validated_data.pop('category')

        category = Category.objects.get(id=category_data.id)
        photo = AppImage.objects.create(**photo_data) if photo_data else None

        item = Item.objects.create(category=category, photo=photo, **validated_data)

        return item

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
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
        
class OrderItemDetailSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'note', 'item_quantity', 'item']
        
class DeliveryPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = '__all__'
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        
        
class NotificationInformationSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'restaurant_name']

    def get_restaurant_name(self, obj):
        return obj.order.restaurant.restaurant_name if obj.order and obj.order.restaurant else None

    def get_message(self, obj):
        return obj.message
    def get_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")