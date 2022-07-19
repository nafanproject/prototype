# Generated by Django 3.2.8 on 2022-07-06 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0040_alter_findingaid_scope_and_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='findingaid',
            name='date',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='digital_link',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='reference_code',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='repository_link',
            field=models.CharField(blank=True, max_length=1255),
        ),
        migrations.AlterField(
            model_name='findingaid',
            name='title',
            field=models.CharField(max_length=1255),
        ),
    ]
