# Generated by Django 5.0.4 on 2024-04-22 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BibliotecaApp', '0002_alter_user_fecha_nacimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcatalogo',
            name='id_catalogo',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]