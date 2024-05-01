# Generated by Django 4.2.11 on 2024-04-29 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('workers', models.ManyToManyField(related_name='services', to='authentication.worker')),
            ],
        ),
    ]
