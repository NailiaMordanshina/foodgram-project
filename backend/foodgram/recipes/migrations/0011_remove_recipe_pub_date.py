# Generated by Django 4.2.5 on 2023-10-01 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_recipe_pub_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='pub_date',
        ),
    ]
