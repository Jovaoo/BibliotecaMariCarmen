# Generated by Django 5.0.4 on 2024-04-19 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BibliotecaApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='fecha_nacimiento',
            field=models.DateField(null=True),
        ),
    ]