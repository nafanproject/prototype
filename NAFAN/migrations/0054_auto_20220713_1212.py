# Generated by Django 3.2.8 on 2022-07-13 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NAFAN', '0053_findingaid_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='findingaid',
            name='creative_commons',
            field=models.CharField(blank=True, max_length=32),
        ),
    ]