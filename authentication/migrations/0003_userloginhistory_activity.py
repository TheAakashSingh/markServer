# Generated by Django 4.2.2 on 2023-06-18 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userloginhistory',
            name='activity',
            field=models.JSONField(null=True),
        ),
    ]
