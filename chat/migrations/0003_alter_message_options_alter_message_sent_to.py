# Generated by Django 5.0.4 on 2024-05-07 11:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_rename_send_by_message_sent_by_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['sent']},
        ),
        migrations.AlterField(
            model_name='message',
            name='sent_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='received', to=settings.AUTH_USER_MODEL),
        ),
    ]
