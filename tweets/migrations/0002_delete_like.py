# Generated by Django 4.1 on 2023-02-19 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tweets", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Like",
        ),
    ]
