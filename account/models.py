from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


class AccountsManager(BaseUserManager):
    def create_user(self, username, email, account_type="CL", password=None):

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            account_type=account_type,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, account_type="AD", password=None):

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            account_type=account_type,
        )

        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


def image_path(instance, filename):
    ext = filename[-4:] if filename[-4] == '.' else '.png'
    return 'account/accounts_images/{0}{1}'.format(instance.username, ext)


class Account(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True)

    email = models.EmailField('Email', unique=True)

    image = models.ImageField('Profile Image', upload_to=image_path, null=True, blank=True)

    account_type = models.CharField(max_length=2, choices={
        "AD": "Admin",  # a smi-total control over the app
        # "SE": "Seller"
        "DL": "Delivery Person",  # those who deliver the items
        "CL": "Client",  # Client
    }, default='CL')
    
    favorite = models.ManyToManyField("item.Item", through="FavoriteItem")

    def list_favorite_item_ids(self):
        """returns a list of the pk of each item in favorite"""
        return [item.pk for item in self.favorite.all()]

    reported = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = AccountsManager()


class FavoriteItem(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="favorite_items")

    item = models.ForeignKey("item.Item", on_delete=models.CASCADE)

    add_date = models.DateTimeField(default=timezone.now)


from chat.models import Chat
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        Chat.objects.create(owner=instance)
