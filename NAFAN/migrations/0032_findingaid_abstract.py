# Generated by Django 3.2.8 on 2022-06-23 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0031_auto_20220614_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='findingaid',
            name='abstract',
            field=models.TextField(blank=True),
        ),
    ]