# Generated by Django 3.2.8 on 2022-06-23 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0032_findingaid_abstract'),
    ]

    operations = [
        migrations.AddField(
            model_name='findingaid',
            name='citation',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
