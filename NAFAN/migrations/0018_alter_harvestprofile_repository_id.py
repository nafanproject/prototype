# Generated by Django 3.2.8 on 2022-04-06 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0017_harvestprofile_harvest_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvestprofile',
            name='repository_id',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
