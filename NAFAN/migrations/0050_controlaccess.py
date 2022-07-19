# Generated by Django 3.2.8 on 2022-07-06 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0049_alter_findingaid_acqinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlAccess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finding_aid_id', models.CharField(blank=True, max_length=32)),
                ('term', models.CharField(blank=True, max_length=255)),
                ('link', models.CharField(blank=True, max_length=1255)),
                ('control_type', models.CharField(blank=True, max_length=1255)),
            ],
        ),
    ]
