# Generated by Django 3.2.8 on 2022-06-23 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0034_findingaid_bioghist'),
    ]

    operations = [
        migrations.AddField(
            model_name='findingaid',
            name='originals_location',
            field=models.TextField(blank=True),
        ),
    ]
