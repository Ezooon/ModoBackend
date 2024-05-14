from rest_framework import decorators
from django.http import FileResponse
from .models import Account


@decorators.api_view(['GET'])
def image(request, filename):
    img = Account.objects.get(image='account/accounts_images/'+filename).image
    r = FileResponse(img, filename=filename)
    return r


@decorators.api_view(['GET'])
def user_image(request, username):
    img = Account.objects.get(username=username).image
    if img:
        r = FileResponse(img, filename=username)
    else:
        r = FileResponse(open("account/accounts_images/default.jpg", 'rb'), filename=username)
    return r
