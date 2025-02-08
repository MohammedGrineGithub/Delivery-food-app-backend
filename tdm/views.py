from django.http import HttpResponse
from rest_framework.generics import CreateAPIView , ListAPIView , RetrieveAPIView , UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import check_password
import random


# # Just for test
def hello(request):
    return HttpResponse("Hello and welcome to our app")

# ================ CREATION FUNCTIONS =================
class CreateUserView(CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_id = response.data.get('id')
        return Response({"message": "User created successfully", "user_id": user_id}, status=status.HTTP_201_CREATED)
    
    
class CreateRestaurantView(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_data = request.data

        # Create logo
        logo_data = restaurant_data.pop('logo', None)
        if logo_data:
            logo_serializer = ImageSerializer(data=logo_data)
            if logo_serializer.is_valid():
                logo = logo_serializer.save()
                restaurant_data['logo'] = logo.id
            else:
                return Response(logo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create banner logo
        banner_logo_data = restaurant_data.pop('banner_logo', None)
        if banner_logo_data:
            banner_logo_serializer = ImageSerializer(data=banner_logo_data)
            if banner_logo_serializer.is_valid():
                banner_logo = banner_logo_serializer.save()
                restaurant_data['banner_logo'] = banner_logo.id 
            else:
                return Response(banner_logo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create location
        location_data = restaurant_data.pop('location', None)
        if location_data:
            location_serializer = LocationSerializer(data=location_data)
            if location_serializer.is_valid():
                location = location_serializer.save()
                restaurant_data['location'] = location.id
            else:
                return Response(location_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create rating
        rating_data = restaurant_data.pop('rating', None)
        if rating_data:
            rating_serializer = RatingSerrializer(data=rating_data)
            if rating_serializer.is_valid():
                rating = rating_serializer.save()
                restaurant_data['rating'] = rating.id
            else:
                return Response(rating_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create menu
        menu_serializer = MenuSerializer(data={})
        if menu_serializer.is_valid():
            menu = menu_serializer.save()
            restaurant_data['menu'] = menu.id
        else:
            return Response(menu_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create restaurant
        restaurant_serializer = RestaurantSerializer(data=restaurant_data)
        if restaurant_serializer.is_valid():
            restaurant_serializer.save()
            return Response(restaurant_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(restaurant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class CreateRestaurantMenu(APIView):
    def post(self, request):
        data = request.data
        restaurant_menu_id = data.get('restaurant_menu')
        if not restaurant_menu_id:
            return Response({"error": "Restaurant menu data not provided"}, status=status.HTTP_400_BAD_REQUEST)
        categories_data = data.get('categories', [])
        for category_data in categories_data:
            category_serializer = CategorySerializer(data={"restaurant_menu": restaurant_menu_id, "name": category_data.get('name')})
            if category_serializer.is_valid():
                category = category_serializer.save()
            else:
                return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            items_data = category_data.get('items', [])
            for item_data in items_data:
                item_serializer = ItemSerializer(data={"category": category.id, **item_data})
                if item_serializer.is_valid():
                    item_serializer.save()
                else:
                    return Response(item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Restaurant menu, categories, and items created successfully"}, status=status.HTTP_201_CREATED)
    
class RestaurantLinksView(APIView):
    def get(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('id')
        if not restaurant_id:
            return Response({"error": "Restaurant ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        
        links = Link.objects.filter(restaurant=restaurant_id)
        serializer = LinkSerializer(links, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
            link_url = link_data.get('url')
            
            if not link_name or not link_url:
                return Response({"error": "Link name or URL not provided for one or more links"}, status=status.HTTP_400_BAD_REQUEST)
            
            link = Link.objects.create(
                restaurant=restaurant,
                name=link_name,
                url=link_url
            )
            created_links.append({"link_name": link.name, "link": link.url})
        
        return Response({"created_links": created_links}, status=status.HTTP_201_CREATED)
    
class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        order_data = request.data.get('order')
        order_items_data = request.data.get('order_items', [])
        user_id = request.data.get('user_id')
        if not order_data:
            return Response({"error": "Order data not provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not order_items_data:
            return Response({"error": "Order items not provided"}, status=status.HTTP_400_BAD_REQUEST)
        delivery_persons = DeliveryPerson.objects.all()
        if not delivery_persons:
            return Response({"error": "No delivery persons available"}, status=status.HTTP_400_BAD_REQUEST)
        delivery_person = random.choice(delivery_persons)
        order_data['delivery_person'] = delivery_person.id
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
        try:
            user = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            order.delete()
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        notification_data = {
            "customer": user.id,
            "message": "Your order is now Waiting",
            "order": order.id
        }
        notification_serializer = NotificationSerializer(data=notification_data)
        if notification_serializer.is_valid():
            notification_serializer.save()
        else:
            order.delete()
            return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user.has_notification = True
        user.save()
        return Response({"message": "Order and order items created successfully"}, status=status.HTTP_201_CREATED)
    
class CreateUserPhotoView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        photo_data = request.data.get('photo')

        if not user_id or not photo_data:
            return Response({"error": "User ID and photo data are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        photo_serializer = ImageSerializer(data=photo_data)
        if photo_serializer.is_valid():
            photo = photo_serializer.save()
            user.photo = photo
            user.save()
            return Response({"message": "Photo created successfully", "photo_id": photo.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class OrderDetailsView(APIView):
    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('id')

        if not order_id:
            return Response({"error": "Order ID and Restaurant ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        restaurant = order.restaurant
        restaurant_data = RestaurantDetailsSerializer(restaurant).data

        order_items = OrderItem.objects.filter(order=order.id)
        order_items_data = OrderItemDetailSerializer(order_items, many=True).data

        delivery_person = order.delivery_person
        delivery_person_data = DeliveryPersonSerializer(delivery_person).data
        
        response_data = {
            "restaurant": restaurant_data,
            "id": order.id,
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": order.status,
            "total_price": order.total_price,
            "delivery_note": order.delivery_note,
            "order_items": order_items_data,
            "delivery_person": delivery_person_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
class CreateMultipleDeliveryPersons(APIView):
    def post(self, request, *args, **kwargs):
        delivery_persons_data = request.data.get('delivery_persons', [])

        if not delivery_persons_data:
            return Response({"error": "No delivery persons data provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_delivery_persons = []
        for delivery_person_data in delivery_persons_data:
            delivery_person_serializer = DeliveryPersonSerializer(data=delivery_person_data)
            if delivery_person_serializer.is_valid():
                delivery_person = delivery_person_serializer.save()
                created_delivery_persons.append(delivery_person_serializer.data)
            else:
                return Response(delivery_person_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"created_delivery_persons": created_delivery_persons}, status=status.HTTP_201_CREATED)
    
    
class CreateMultipleCuisineTypes(APIView):
    def post(self, request, *args, **kwargs):
        cuisine_types_data = request.data.get('cuisine_types', [])

        if not cuisine_types_data:
            return Response({"error": "No cuisine types data provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_cuisine_types = []
        for cuisine_type_data in cuisine_types_data:
            cuisine_type_serializer = CuisinTypeSerializer(data=cuisine_type_data)
            if cuisine_type_serializer.is_valid():
                cuisine_type = cuisine_type_serializer.save()
                created_cuisine_types.append(cuisine_type_serializer.data)
            else:
                return Response(cuisine_type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"created_cuisine_types": created_cuisine_types}, status=status.HTTP_201_CREATED)
    
class CreateMultipleWilayas(APIView):
    def post(self, request, *args, **kwargs):
        wilayas_data = request.data.get('wilayas', [])

        if not wilayas_data:
            return Response({"error": "No wilayas data provided"}, status=status.HTTP_400_BAD_REQUEST)

        created_wilayas = []
        for wilaya_data in wilayas_data:
            wilaya_serializer = WilayaSerializer(data=wilaya_data)
            if wilaya_serializer.is_valid():
                wilaya = wilaya_serializer.save()
                created_wilayas.append(wilaya_serializer.data)
            else:
                return Response(wilaya_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"created_wilayas": created_wilayas}, status=status.HTTP_201_CREATED)
    
# =================================================================================


# ========================= USER FUNCTIONS =======================================
class CustomerInformation(RetrieveAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = 'id'
    
class CustomerUpdateView(APIView):
    def put(self, request, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EmailLoginView(APIView):
    def post(self, request):
        serializer = UserEmailLoginSerializer(data=request.data)
        if serializer.validate(request.data):
            try:
                user = Customer.objects.get(email=request.data['email'])
                if not user.is_active:
                    return Response({"error": "Account is not active"}, status=status.HTTP_403_FORBIDDEN)
                return Response({"message": "User logged in successfully.", "user_id": user.id}, status=status.HTTP_202_ACCEPTED)
            except Customer.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class RestaurantCommentsView(APIView):
    def get(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('id')
        if not restaurant_id:
            return Response({"error": "Restaurant ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        rating_id = restaurant.rating.id 
        comments = Comment.objects.filter(rating=rating_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    
    
class CustomerNotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found "}, status=status.HTTP_404_NOT_FOUND)
        
        notifications = Notification.objects.filter(customer=customer_id).order_by('created_at')
        serializer = NotificationInformationSerializer(notifications, many=True)
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
            restaurant_data = RestaurantDetailsSerializer(restaurant).data
            order_data = OrderSerializer(order).data
            order_data['restaurant'] = restaurant_data
            order_data['created_at'] = order.created_at.strftime("%Y-%m-%d %H:%M:%S")
            response_data.append(order_data)
        
        return Response(response_data, status=status.HTTP_200_OK)
 

class HasNotificationView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"has_notification": user.has_notification}, status=status.HTTP_200_OK)   
class ChangeCustomerPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        customer_id = request.data.get('id')
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not customer_id or not current_password or not new_password:
            return Response({"error": "Customer ID, current password, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        if not check_password(current_password, customer.password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        customer.set_password(new_password)
        customer.save()

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK) 
# =================================================================================
    
# ========================= RESTAURANT FUNCTIONS =======================================
class RestaurantDetails(RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailsSerializer
    lookup_field = 'id'
    
class SearchingForRestaurant(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_name = request.data.get('restaurant_name', None)
        if restaurant_name:
            restaurants = Restaurant.objects.filter(restaurant_name__icontains=restaurant_name)
            serializer = RestaurantDetailsSerializer(restaurants, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "restaurant_name not provided"}, status=status.HTTP_400_BAD_REQUEST)
    
class FilterRestaurant(APIView):
    def post(self, request, *args, **kwargs):
        wilaya = request.data.get('wilaya', None)
        cuisine = request.data.get('cuisine', None)
        
        if wilaya and cuisine:
            restaurants = Restaurant.objects.filter(location__wilaya=wilaya, cuisine_type=cuisine)
        elif wilaya:
            restaurants = Restaurant.objects.filter(location__wilaya=wilaya)
        elif cuisine:
            restaurants = Restaurant.objects.filter(cuisine_type=cuisine)
        else:
            return Response({"error": "Neither wilaya nor cuisine provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RestaurantDetailsSerializer(restaurants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   
class DeleteCustomerNotificationsView(APIView):
    def delete(self, request, *args, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        notifications = Notification.objects.filter(customer=customer_id)
        notifications.delete()
        
        return Response({"message": "Notifications deleted successfully"}, status=status.HTTP_200_OK)
class DeleteCustomerOrdersView(APIView):
    def delete(self, request, *args, **kwargs):
        customer_id = kwargs.get('id')
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        orders = Order.objects.filter(customer=customer)
        orders.delete()

        return Response({"message": "Customer orders deleted successfully"}, status=status.HTTP_200_OK)
class RestaurantMenuView(APIView):
    def get(self, request, *args, **kwargs):
        menu_id = kwargs.get('id')
        if not menu_id:
            return Response({"error": "Restaurant ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        categories = Category.objects.filter(restaurant_menu=menu_id)
        response_data = []
        
        for category in categories:
            items = Item.objects.filter(category=category)
            category_data = {
                "id" : category.id,
                "name": category.name,
                "items": ItemSerializer(items, many=True).data
            }
            response_data.append(category_data)
        
        return Response(response_data, status=status.HTTP_200_OK)

class Restaurants(ListAPIView) :
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantDetailsSerializer

class RateRestaurantView(APIView):
    def post(self, request, *args, **kwargs):
        restaurant_id = request.data.get('id')
        user_rating = request.data.get('rating')
        user_comment = request.data.get('comment')
        order_id = request.data.get('order_id')

        if not restaurant_id or not user_rating:
            return Response({"error": "Restaurant ID and rating are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        rating, _ = Rating.objects.get_or_create(restaurant=restaurant.id)
        rating.reviewers_count += 1
        rating.rating = ( rating.rating * (rating.reviewers_count - 1) + user_rating ) / rating.reviewers_count
        rating.save()
        user_comment= user_comment.lstrip()
        if len(user_comment) > 0:
            Comment.objects.create(
                comment=user_comment,
                rating=rating
            )
        order.status = 6
        order.save()
        return Response({"message": "Rating and comment added successfully"}, status=status.HTTP_201_CREATED)



# ================================================================================= 
    
class UpdateHasNotificationView(APIView):
    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('id')
        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Customer.objects.get(id=user_id)
        except Customer.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user.has_notification = False
        user.save()
        return Response({"message": "User notification status changed successfully"}, status=status.HTTP_200_OK)

# ========================= INTERMÉDIAIRE FUNCTIONS =======================================

class ChangeOrderStatusView(APIView):
    STATUS_MESSAGES = {
        0: 'Waiting',
        1: 'Prepared',
        2: 'Picked Up',
        3: 'On Way',
        4: 'Delivered',
        5: 'Canceled',
        6: 'Rated'
    }
    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        new_status = request.data.get('status')
        user_id = request.data.get('user_id')

        if not order_id or not new_status or not user_id :
            return Response({"error": "Order ID and new status are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = Customer.objects.get(id=user_id)
        except Order.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        order.status = new_status
        user.has_notification = True
        order.save()
        user.save()

        if new_status != 6 :
            status_message = self.STATUS_MESSAGES.get(new_status, 'Unknown')
            message = f"Your order is now {status_message}"
            notification_data = {
                "customer": user.id,
                "message": message,
                "order": order.id
            }
            notification_serializer = NotificationSerializer(data=notification_data)
            if notification_serializer.is_valid():
                notification_serializer.save()
            else:
                return Response(notification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Order status changed successfully"}, status=status.HTTP_200_OK)
    
# =================================================================================
class UpdateCustomerViewv2(APIView):
        def put(self, request, *args, **kwargs):
            customer_id = kwargs.get('id')
            if not customer_id:
                return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class UpdateCustomerPhoneNumberView(APIView):
    def put(self, request, *args, **kwargs):
        # Extract customer_id from URL kwargs
        customer_id = kwargs.get('id')
        
        # Check if customer_id is provided
        if not customer_id:
            return Response({"error": "Customer ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if 'phone' is provided in the request data
        new_phone_number = request.data.get('phone')
        if not new_phone_number:
            return Response({"error": "Phone number not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the customer object
            customer = Customer.objects.get(id=customer_id)
            
            # Update the phone number
            customer.phone = new_phone_number
            customer.save()
            
            # Return success response
            return Response({"message": "Phone number updated successfully"}, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:
            # Handle case where customer does not exist
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            # Handle any other unexpected errors
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllCuisineTypesView(ListAPIView):
    queryset = CuisingType.objects.all()
    serializer_class = CuisinTypeSerializer

class AllWilayasView(ListAPIView):
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializerAll

class AllDeliveryPersons(ListAPIView):
    queryset = DeliveryPerson.objects.all()
    serializer_class = DeliveryPersonSerializer


class UpdateRestaurantTimingsView(APIView):
        def put(self, request, *args, **kwargs):
            restaurant_id = kwargs.get('id')
            opening_time = request.data.get('opening_time')
            closing_time = request.data.get('closing_time')

            if not restaurant_id or not opening_time or not closing_time:
                return Response({"error": "Restaurant ID, opening time, and closing time are required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Restaurant.DoesNotExist:
                return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

            restaurant.opening_time = opening_time
            restaurant.closing_time = closing_time
            restaurant.save()

            return Response({"message": "Restaurant timings updated successfully"}, status=status.HTTP_200_OK)