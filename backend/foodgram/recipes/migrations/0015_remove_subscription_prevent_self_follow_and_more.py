# Generated by Django 4.2.5 on 2023-10-05 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0014_merge_20231003_1620'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='subscription',
            name='prevent_self_follow',
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(help_text='Пользователь', on_delete=django.db.models.deletion.CASCADE, related_name='shopping_user', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
