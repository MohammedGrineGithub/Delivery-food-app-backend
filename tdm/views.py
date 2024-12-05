from django.http import JsonResponse
from rest_framework.generics import CreateAPIView , ListAPIView , RetrieveAPIView , UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.filters import SearchFilter



class CreateUserView(CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = UserCreationSerializer
    
    
class EmailLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserEmailLoginSerializer(data = request.data)
        if serializer.validate(request.data):
            return Response({"message": "User logged in successfully."}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
class PhoneNumberLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserPhoneLoginSerializer(data = request.data)
        if serializer.validate(request.data):
            return Response({"message": "User logged in successfully."}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

       
class CustomTokenObtainPairViewForEmailAuthentication(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializerForEmail
    
    
class CustomTokenObtainPairViewForPhoneAuthentication(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializerPhoneNumber    
        
        
class SearchingRestaurant(ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [SearchFilter]
    search_fields = ['restaurant_name']
    
    
class Restaurants(ListAPIView) :
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    
    
class FilterRestaurantsByCuisineType(RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    lookup_field = 'cuisine_type'
    
    
class FilterRestaurantsByWilaya(ListAPIView):
    serializer_class = RestaurantSerializer
    lookup_field = 'wilaya'
    def get_queryset(self):
        return Restaurant.objects.select_related('location')


class CustomerInformation(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'phone'
    
    
class CustomerUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    
class LocationUpdateView(UpdateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    
    
class ImgaeUpdateView(UpdateAPIView):
    queryset = AppImage.objects.all()
    serializer_class = ImageSerializer