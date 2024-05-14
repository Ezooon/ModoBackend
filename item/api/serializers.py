from rest_framework.serializers import ModelSerializer, ImageField, StringRelatedField
from ..models import Item, Cart, CartItem, Category
from chat.api.serializers import Message, MessageSerializer
from account.models import Account


class ItemSerializer(ModelSerializer):
    image = ImageField(use_url=True)
    category = StringRelatedField()

    class Meta:
        model = Item
        fields = ["id", "name", "description", "price", "image", "category", "add_by", "stock"]


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class CartItemSerializer(ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CartItem
        fields = ["id", "item", "price", "amount"]


class CreateCartItemSerializer(ModelSerializer):

    class Meta:
        model = CartItem
        fields = ["id", "item", "amount"]


class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ["id", "cart_items", "add_date", "delivered"]


class CreateCartSerializer(ModelSerializer):
    cart_items = CreateCartItemSerializer(many=True)
    message = MessageSerializer(required=False)

    class Meta:
        model = Cart
        fields = ["id", "user", "cart_items", "message", "add_date"]

    def create(self, validated_data):
        self.is_valid()
        c_items_data = validated_data.pop("cart_items")
        c_items = []
        items = []

        cart = Cart.objects.create(**validated_data)

        short = []  # short-of-stock
        oos = []  # out-of-stock items
        for data in c_items_data:
            item = data["item"]
            if item.stock <= 0:
                oos.append(item.name)
                continue

            data["cart"] = cart
            data["price"] = item.price

            if data["amount"] <= item.stock:
                item.stock -= data["amount"]
            else:
                short.append(f"you ordered {data['amount']} of {item.name} but only {item.stock} left.")
                data["amount"] = item.stock
                item.stock = 0
            items.append(item)

            c_items.append(CartItem(**data))

        Item.objects.bulk_update(items, ['stock'])
        cart.cart_items.bulk_create(c_items)

        cart.message = Message.objects.create(chat=cart.user.chat, sent_by=cart.user, content=str(cart))

        # ToDo Have a dedicated user to send these messages
        Message.objects.create(chat=cart.user.chat, sent_by=Account.objects.get(pk=1), sent_to=cart.user,
                               content="{0} {1} out of stock.\n{2}".format(
                                   " & ".join(oos),
                                   "are" if len(oos) > 1 else "is",
                                   '\n'.join(short)))
        cart.save()

        return cart
