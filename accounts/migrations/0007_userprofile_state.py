# Generated by Django 4.1.2 on 2023-03-10 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_userprofile_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
