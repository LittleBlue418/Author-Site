# Generated by Django 3.1 on 2020-09-23 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('series', '0001_initial'),
        ('fan_art', '0003_auto_20200910_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fanart',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fan_art', to='series.series'),
        ),
    ]
