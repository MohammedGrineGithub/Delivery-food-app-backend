from django.http import HttpResponse

# # Just for test
def hello(request):
    return HttpResponse("Hello and welcome to our app")