# Generated by Django 5.0.3 on 2024-04-02 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0010_notification_seen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demand',
            name='price',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='offering',
            name='price',
            field=models.IntegerField(default=0, null=True),
        ),
    ]