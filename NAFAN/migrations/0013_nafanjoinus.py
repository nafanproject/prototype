# Generated by Django 3.2.8 on 2022-03-30 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0012_repository_snac_permalink'),
    ]

    operations = [
        migrations.CreateModel(
            name='NAFANJoinUs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=25)),
                ('url', models.CharField(blank=True, max_length=255)),
                ('collection_guides', models.TextField()),
                ('multiple_organizations', models.CharField(max_length=25)),
            ],
        ),
    ]
