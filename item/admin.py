from django.contrib import admin
from .models import Item, Cart, CartItem, Category


class AddCartItem(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['item', 'amount']


class CartAdmin(admin.ModelAdmin):
    # list_display = ('owner',)

    inlines = [AddCartItem]


admin.site.register(Item)
admin.site.register(Category)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)

# Register your models here.
