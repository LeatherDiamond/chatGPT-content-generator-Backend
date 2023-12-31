# Generated by Django 4.2.4 on 2023-08-24 12:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("gpt_generator", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="generatedresponse",
            name="file_name",
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="generatedimage",
            name="image",
            field=models.ImageField(upload_to=""),
        ),
    ]
