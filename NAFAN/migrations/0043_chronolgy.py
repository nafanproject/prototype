# Generated by Django 3.2.8 on 2022-07-06 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0042_findingaid_intra_repository'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chronolgy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finding_aid_id', models.CharField(blank=True, max_length=32)),
                ('date', models.CharField(blank=True, max_length=255)),
                ('event', models.CharField(blank=True, max_length=1255)),
            ],
        ),
    ]