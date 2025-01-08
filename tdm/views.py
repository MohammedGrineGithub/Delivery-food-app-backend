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
    serializer_class = CustomerSerializer
    
    
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
# restaurant functions         
class CreateRestaurant(CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    
class CreateRestaurantMenu(CreateAPIView):
    queryset = RestaurantMenu.objects.all()
    serializer_class = RestaurantMenuCreationSerializer
    
class RestaurantMenuView(APIView):
    def get(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('id')
        if not restaurant_id:
            return Response({"error": "Restaurant ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        
        menu = RestaurantMenu.objects.filter(restaurant=restaurant)
        categories = Category.objects.filter(menu__in=menu)
        response_data = []
        
        for category in categories:
            items = Item.objects.filter(category=category)
            category_data = {
                "category": category.name,
                "items": ItemSerializer(items, many=True).data
            }
            response_data.append(category_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
class CreateMultipleRestaurantLinks(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_id = request.data.get('id')
        links = request.data.get('links', [])
        
        if not restaurant_id:
            return Response({"error": "Restaurant ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not links:
            return Response({"error": "No links provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        
        created_links = []
        for link_data in links:
            link_name = link_data.get('name')
            link_url = link_data.get('link')
            
            if not link_name or not link_url:
                return Response({"error": "Link name or URL not provided for one or more links"}, status=status.HTTP_400_BAD_REQUEST)
            
            link = Link.objects.create(
                restaurant=restaurant,
                name=link_name,
                url=link_url
            )
            created_links.append({"link_name": link.name, "link": link.url})
        
        return Response({"created_links": created_links}, status=status.HTTP_201_CREATED)
class RestaurantOverView(RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantOverViewSerializer
    lookup_field = 'id'
    
class SearchingForRestaurant(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_name = request.data.get('restaurant_name', None)
        if restaurant_name:
            restaurants = Restaurant.objects.filter(restaurant_name__icontains=restaurant_name)
            serializer = RestaurantOverViewSerializer(restaurants, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "restaurant_name not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class FilterRestaurant(APIView):
    def post(self, request, *args, **kwargs):
        wilaya = request.data.get('wilaya', None)
        cuisine = request.data.get('cuisine', None)
        
        if wilaya and cuisine:
            restaurants = Restaurant.objects.filter(location__wilaya=wilaya, cuisine_type__name=cuisine)
        elif wilaya:
            restaurants = Restaurant.objects.filter(location__wilaya=wilaya)
        elif cuisine:
            restaurants = Restaurant.objects.filter(cuisine_type__name=cuisine)
        else:
            return Response({"error": "Neither wilaya nor cuisine provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RestaurantOverViewSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class Restaurants(ListAPIView) :
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantOverViewSerializer
 #  ----------------------------------------------   

# customer functions
class CustomerInformation(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'id'
    
    
class CustomerUpdateView(UpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    
class LocationUpdateView(UpdateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
class CustomerNotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        notifications = Notification.objects.filter(customer=customer)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CustomerOrdersView(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        orders = Order.objects.filter(customer=customer)
        response_data = []
        
        for order in orders:
            restaurant = order.restaurant
            restaurant_data = RestaurantOverViewSerializer(restaurant).data
            order_data = OrderSerializer(order).data
            order_data['restaurant'] = restaurant_data
            response_data.append(order_data)
        
        return Response(response_data, status=status.HTTP_200_OK)

class RateRestaurantView(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_id = request.data.get('id')
        user_rating = request.data.get('rating')
        user_comment = request.data.get('comment')

        if not restaurant_id or not user_rating:
            return Response({"error": "Restaurant ID and rating are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

        rating, created = Rating.objects.get_or_create(restaurant=restaurant)
        rating.reviewers_count += 1
        rating.rating = rating.rating + ( user_rating / rating.reviewers_count ) 
        rating.save()

        Comment.objects.create(
            comment=user_comment,
            rating=rating.id
        )

        return Response({"message": "Rating and comment added successfully"}, status=status.HTTP_201_CREATED)
    
    
class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        order_data = request.data.get('order')
        order_items_data = request.data.get('order_items', [])

        if not order_data:
            return Response({"error": "Order data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not order_items_data:
            return Response({"error": "Order items not provided"}, status=status.HTTP_400_BAD_REQUEST)

        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for item_data in order_items_data:
            item_data['order'] = order.id
            order_item_serializer = OrderItemSerializer(data=item_data)
            if order_item_serializer.is_valid():
                order_item_serializer.save()
            else:
                order.delete()
                return Response(order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Order and order items created successfully"}, status=status.HTTP_201_CREATED)