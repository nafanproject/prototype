# Generated by Django 3.2.8 on 2022-06-23 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0033_findingaid_citation'),
    ]

    operations = [
        migrations.AddField(
            model_name='findingaid',
            name='bioghist',
            field=models.TextField(blank=True),
        ),
    ]
