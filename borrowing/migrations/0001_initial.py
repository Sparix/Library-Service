# Generated by Django 5.0.1 on 2024-01-23 14:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("books", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Borrowing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("borrowing_date", models.DateField(auto_now_add=True)),
                ("expected_return_date", models.DateField()),
                (
                    "actual_return_date",
                    models.DateField(blank=True, default=None, null=True),
                ),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borrowing_book",
                        to="books.books",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="borrowing_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("borrowing_date__gt", models.F("expected_return_date"))
                ),
                name="borrowing date can't be earlier than expected return date",
            ),
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                check=models.Q(("borrowing_date__gte", models.F("actual_return_date"))),
                name="borrowing date can't be earlier than actual return date",
            ),
        ),
    ]
