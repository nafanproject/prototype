# Generated by Django 3.2.8 on 2022-06-02 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0021_auto_20220526_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_repositories',
            name='st_city',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user_repositories',
            name='state',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
