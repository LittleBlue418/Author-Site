# Generated by Django 3.1 on 2020-09-25 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0003_auto_20200925_1940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stripe_payment_id',
            field=models.CharField(max_length=254, unique=True),
        ),
    ]