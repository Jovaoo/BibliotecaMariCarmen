# Generated by Django 5.0.4 on 2024-04-25 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BibliotecaApp', '0002_user_has_password_changed'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcatalogo',
            name='cantidad',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='itemcatalogo',
            name='cantidad_disponible',
            field=models.IntegerField(default=0),
        ),
    ]
