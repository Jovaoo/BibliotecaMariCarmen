# Generated by Django 4.2.11 on 2024-04-20 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BibliotecaApp', '0005_alter_libro_coleccion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libro',
            name='paginas',
            field=models.IntegerField(default=0),
        ),
    ]
