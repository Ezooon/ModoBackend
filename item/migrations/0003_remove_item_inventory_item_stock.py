# Generated by Django 5.0.4 on 2024-04-12 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0002_remove_cart_item_cart_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='inventory',
        ),
        migrations.AddField(
            model_name='item',
            name='stock',
            field=models.IntegerField(default=1, verbose_name='in stock'),
            preserve_default=False,
        ),
    ]
