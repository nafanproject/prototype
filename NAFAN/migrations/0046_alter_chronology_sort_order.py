# Generated by Django 3.2.8 on 2022-07-06 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0045_chronology_sort_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chronology',
            name='sort_order',
            field=models.IntegerField(),
        ),
    ]