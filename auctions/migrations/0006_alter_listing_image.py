# Generated by Django 3.2.8 on 2021-11-17 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_listing_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
    ]