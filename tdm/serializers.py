from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import datetime


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['full_name', 'password', 'email' , 'phone' ]
    def validate_email(self,value) :
        if Customer.objects.filter(username=value).exists() :
            return serializers.ValidationError("Email is already taken.")
    def validate_phone(self,value):
        if Customer.objects.filter(phone=value).exists() :
            return serializers.ValidationError("Phone number is already taken.")
    def create(self, validated_data):
        user = Customer(
            username=validated_data['full_name'],
            email=validated_data['email'],
            phone = validated_data['phone']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
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
    class Meta :
        model = AppImage
        fields = [ 'image']
class LocationSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Location
        fields = [ 'wilaya' , 'address' , 'map_link']
class RestaurantSerializer(serializers.ModelSerializer) :
    rating = RatingSerrializer
    logo = ImageSerializer
    class Meta :
        model = Restaurant 
        fields = [ 'id' , 'logo' , 'restaurant_name' , 'rating' , 'deldelivery_price' , 'delivery_duration' ]
class CustomerSerializer(serializers.ModelSerializer):
    photo = ImageSerializer
    location = LocationSerializer
    class Meta :
        model = Customer
        fields =  [ 'full_name' , 'phone' , 'location' , 'photo']