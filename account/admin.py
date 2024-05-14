from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, FavoriteItem


class AddFavoratieItem(admin.StackedInline):
    model = FavoriteItem
    extra = 0
    fields = ['item', 'add_date']


class AccountAdmin(UserAdmin):
    list_display = ('username', 'email')
    search_fields = ('username',)
    ordering = ('username',)
    fieldsets = (
        ("Info", {'fields': ('image', 'username', 'email', 'password',)}),
        ("Settings", {'fields': ('account_type',)}),
    )
    inlines = [AddFavoratieItem]
    # add_fieldsets = fieldsets


# Register your models here.
admin.site.register(Account, AccountAdmin)


# Register your models here.
