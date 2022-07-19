# Generated by Django 3.2.8 on 2022-04-05 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0014_auto_20220331_1201'),
    ]

    operations = [
        migrations.CreateModel(
            name='AidProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository_id', models.IntegerField()),
                ('governing_access', models.TextField(blank=True)),
                ('rights', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='HarvestProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repository_id', models.IntegerField()),
                ('harvest_location', models.CharField(blank=True, max_length=255)),
                ('default_format', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
