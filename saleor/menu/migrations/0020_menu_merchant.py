# Generated by Django 3.1.2 on 2021-02-20 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0001_initial'),
        ('menu', '0019_menu_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='merchant',
            field=models.ForeignKey(default=5, on_delete=django.db.models.deletion.CASCADE, to='merchant.merchant'),
            preserve_default=False,
        ),
    ]
