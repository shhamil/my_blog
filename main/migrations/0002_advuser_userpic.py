# Generated by Django 2.2.14 on 2020-10-01 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='advuser',
            name='userpic',
            field=models.ImageField(blank=True, upload_to='images/', verbose_name='Аватарка'),
        ),
    ]
