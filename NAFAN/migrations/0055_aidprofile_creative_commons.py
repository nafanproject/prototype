# Generated by Django 3.2.8 on 2022-07-13 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0054_auto_20220713_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='aidprofile',
            name='creative_commons',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]
