from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth = JWTAuthentication()
    def __call__(self, request):
        if request.path.startswith('/user/') :
            try:
                user, token = self.auth.authenticate(request)
                request.user = user
            except AuthenticationFailed:
                return JsonResponse({"detail": "Invalid or missing token"}, status=401)
        response = self.get_response(request)
        return response
