from rest_framework import decorators
from django.http import FileResponse
from .models import Item


@decorators.api_view(['GET'])
def image(request, filename):
    img = Item.objects.get(image='item/item_images/'+filename).image
    r = FileResponse(img, filename=filename)
    return r
