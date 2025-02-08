from django.urls import path , include
from .views import hello
from . import views
from rest_framework_simplejwt.views import TokenRefreshView , TokenVerifyView
urlpatterns = [ 
    path('', hello),
    path('api/token/', include([
        path('email/', views.CustomTokenObtainPairViewForEmailAuthentication.as_view(), name='token_obtain_pair'),
        path('phone_number/', views.CustomTokenObtainPairViewForPhoneAuthentication.as_view(), name='token_obtain_pair'),
        path('verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ]) ),         
    path('restaurant/', include([
        path('all/', views.Restaurants.as_view(), name='restaurants_overview'),
        path('details/<int:id>/', views.RestaurantDetails.as_view(), name='restaurant_detail'),
        path('filter/', views.FilterRestaurant.as_view(), name='restaurant_filter'),
        path('search/', views.SearchingForRestaurant.as_view(), name='restaurant_search'),
        path('menu/<int:id>/', views.RestaurantMenuView.as_view(), name='restaurant_menu'),
        path('links/<int:id>/', views.RestaurantLinksView.as_view(), name='restaurant_links'),
        path('comments/<int:id>/', views.RestaurantCommentsView.as_view(), name='restaurant_comments'),
        ])),
    path('user/', include([
        path('register/', views.CreateUserView.as_view(), name='register_user'),
        path('login/', views.EmailLoginView.as_view(), name='login_user'),
        path('details/<int:id>/', views.CustomerInformation.as_view(), name='user_details'),
        path('update/<int:id>/', views.CustomerUpdateView.as_view(), name='user_update'),
        path('update/phone/<int:id>/', views.UpdateCustomerPhoneNumberView.as_view(), name='user_update_phone'),
        path('updatev2/<int:id>/', views.UpdateCustomerViewv2.as_view(), name='user_updatev2'),
        path('notifications/<int:id>/', views.CustomerNotificationsView.as_view(), name='user_notifications'),
        path('rate_order/', views.RateRestaurantView.as_view(), name='rate_order'),
        path('order_history/<int:id>/', views.CustomerOrdersView.as_view(), name='order_history'),
        path('order/', views.CreateOrderView.as_view(), name='order'),
        path('change_password/', views.ChangeCustomerPasswordView.as_view(), name='change_password'),
        path('order_detail/<int:id>/', views.OrderDetailsView.as_view(), name='order_detail'),
        path('update_has_notifications/<int:id>/', views.UpdateHasNotificationView.as_view(), name='update_has_notifications'),
        path('delete_notifications/<int:id>/', views.DeleteCustomerNotificationsView.as_view(), name='delete_user"s_notifications'),
        path('delete_orders/<int:id>/', views.DeleteCustomerOrdersView.as_view(), name='delete_user"s_orders'),
        path('create_photo/', views.CreateUserPhotoView.as_view(), name='create_photo'),
        path('has_notification/<int:id>/', views.HasNotificationView.as_view(), name='has_notification'),
        ])),
    path('create/', include([
        path('wilaya/', views.CreateMultipleWilayas.as_view(), name='wilaya_create'),
        path('cuisine_type/', views.CreateMultipleCuisineTypes.as_view(), name='cuisine_type_create'),
        path('restaurant/', views.CreateRestaurantView.as_view(), name='restaurant_create'),
        path('restaurant_menu/', views.CreateRestaurantMenu.as_view(), name='restaurant_menu_create'),
        path('restaurant/links/', views.CreateMultipleRestaurantLinks.as_view(), name='restaurant_links_create'),
        path('restaurant/deliveries/', views.CreateMultipleDeliveryPersons.as_view(), name='customer_create'),
        ]),
    ),
    path('app/', include([ 
     path('change_status/', views.ChangeOrderStatusView.as_view(), name='change_status'),
     path('all_cuisine_types/', views.AllCuisineTypesView.as_view(), name='all_cuisine_types'),  
     path('update_restaurant_opening_time/<int:id>/', views.UpdateRestaurantTimingsView.as_view(), name='update_restaurant_opening_time'),                   
    ])),
]