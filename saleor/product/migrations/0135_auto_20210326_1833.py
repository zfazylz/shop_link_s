# Generated by Django 3.1.2 on 2021-03-26 18:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0134_merchantvisiblecategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchantvisiblecategory',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merchants', to='product.category'),
        ),
    ]
