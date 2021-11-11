# Generated by Django 3.2.8 on 2021-11-03 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userreviews', '0006_systemaccount_date_password_change'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('path', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
