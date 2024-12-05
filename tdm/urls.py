from django.urls import path , include
from . import views
from rest_framework_simplejwt.views import TokenRefreshView , TokenVerifyView
urlpatterns = [ 
    path('api/token/', include([
        path('email/', views.CustomTokenObtainPairViewForEmailAuthentication.as_view(), name='token_obtain_pair'),
        path('phone_number/', views.CustomTokenObtainPairViewForPhoneAuthentication.as_view(), name='token_obtain_pair'),
        path('verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ]) ),         
    path('user/', include([
        ])),
    path('creation/', views.CreateUserView.as_view(), name="user_creation"),
    path('login/email/',views.EmailLoginView.as_view(),name="login_by_email"),
    path('login/phone_number/', views.PhoneNumberLoginView.as_view(), name="login_by_phone_number") ,
]