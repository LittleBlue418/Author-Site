# Generated by Django 3.1 on 2020-09-23 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='stripe_payment_id',
            field=models.CharField(max_length=254),
        ),
    ]
