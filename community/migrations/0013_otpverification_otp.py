# Generated by Django 5.0.3 on 2024-04-03 23:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0012_otpverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='otpverification',
            name='otp',
            field=models.CharField(default=0, max_length=6),
        ),
    ]