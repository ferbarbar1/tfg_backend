# Generated by Django 4.2.11 on 2024-09-06 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='stripe_session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
