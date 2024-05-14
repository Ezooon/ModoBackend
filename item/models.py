import json

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone, crypto
from django.db.models.signals import pre_save


# Create your models here.


# class Category(models.Model):
#     name = models.CharField('Category Name', max_length=20, unique=True)
#     icon_name = models.CharField(max_length=40)
#
#     def __str__(self):
#         return self.name


def item_image_path(instance, filename):
    return 'item/item_images/{0}_{1}'.format(instance.id, filename)
    # return 'item/item_images/item_{0}/{0}_{1}'.format(instance.product.id, filename) ToDo do this for if you added
    #                                                                                     more images to an item


class Category(models.Model):
    name = models.CharField('Category Name', max_length=20, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField('Product Name', max_length=100, )

    description = models.TextField('Description', blank=True, null=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)

    image = models.ImageField(upload_to=item_image_path)

    stock = models.IntegerField('in stock')

    add_by = models.ForeignKey('account.Account', default=None, on_delete=models.CASCADE)

    last_modified = models.DateTimeField(default=timezone.now)

    # tags = models.ManyToManyField(Tag, on_delete=models.SET_NULL, null=True, default=None)
    # ToDo keep stacking the tags on the user's account, and use the most repeated to target :)

    # slug = models.SlugField(null=True, unique=True, max_length=25)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, default=None)
    # default to 'others'

    def __str__(self):
        return f"{self.stock} of {self.name}"


class Cart(models.Model):
    user = models.ForeignKey("account.Account", on_delete=models.CASCADE, related_name="ordered_carts")

    items = models.ManyToManyField(Item, through="item.CartItem")

    add_date = models.DateTimeField(default=timezone.now)

    message = models.ForeignKey(to="chat.Message", on_delete=models.SET_NULL, null=True, blank=True)

    delivered = models.DateTimeField(null=True, blank=True)

    # keeper = models.ForeignKey("account.Account", on_delete=models.DO_NOTHING, related_name="kept_carts")
    # ToDo add this keeper field to track who's the item with at the moment.

    @property
    def count(self):
        return sum(citem.amount for citem in self.cart_items.all())

    @property
    def total(self):
        return sum(citem.amount * citem.price for citem in self.cart_items.all())

    def __str__(self):
        return "C" + json.dumps({
            "id": self.id,
            "items": [
                {
                    "item": c_item.item.id,
                    "price": float(c_item.price),
                    "amount": c_item.amount
                } for c_item in self.cart_items.all()]
        })


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=8, decimal_places=2)

    amount = models.IntegerField('number of units', default=1)
