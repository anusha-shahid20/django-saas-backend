from django.http import HttpResponse


def hello_backend(request):
    return HttpResponse("Hello Backend")