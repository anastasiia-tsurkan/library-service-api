# Generated by Django 4.2.1 on 2023-05-06 17:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowings", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return",
            field=models.DateField(blank=True, null=True),
        ),
    ]
