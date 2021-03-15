# Generated by Django 3.1.2 on 2021-03-14 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0002_auto_20210307_1305'),
        ('product', '0133_auto_20210308_1855'),
    ]

    operations = [
        migrations.CreateModel(
            name='MerchantVisibleCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.category')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchant.merchant')),
            ],
            options={
                'unique_together': {('category', 'merchant')},
            },
        ),
    ]
