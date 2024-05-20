from django.http import HttpResponseRedirect, FileResponse


def home_view(request, *args):
    return HttpResponseRedirect("get_modo/", content="Enjoy Modo!")


def download_view(request, *args):
    return FileResponse(open("account/accounts_images/default.jpg", 'rb'), filename="client.apk")
