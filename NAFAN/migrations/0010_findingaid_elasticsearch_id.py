# Generated by Django 3.2.8 on 2022-03-09 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0009_auto_20220308_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='findingaid',
            name='elasticsearch_id',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]