# Generated by Django 3.2.8 on 2022-07-11 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0051_findingaid_container'),
    ]

    operations = [
        migrations.AlterField(
            model_name='findingaid',
            name='container',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='custodhist',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='processinfo',
            field=models.CharField(blank=True, max_length=1255),
        ),
    ]
