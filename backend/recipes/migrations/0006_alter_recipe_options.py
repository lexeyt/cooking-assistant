# Generated by Django 3.2.3 on 2024-02-08 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240208_2236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['creation_date'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
