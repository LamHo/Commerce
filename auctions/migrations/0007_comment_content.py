# Generated by Django 3.2.8 on 2021-11-18 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_listing_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='content',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
