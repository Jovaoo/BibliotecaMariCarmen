# Generated by Django 4.2.11 on 2024-04-20 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('BibliotecaApp', '0003_alter_itemcatalogo_id_catalogo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libro',
            name='ISBN',
            field=models.CharField(max_length=30),
        ),
    ]
