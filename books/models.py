from django.db import models


class Genres(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Authors(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Books(models.Model):
    class CoverChoices(models.TextChoices):
        SOFT = "soft", "SOFT"
        HARD = "hard", "HARD"

    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        Authors, on_delete=models.SET_NULL, related_name="books_author", null=True
    )
    genre = models.ManyToManyField(
        Genres,
        related_name="books_genre",
    )
    cover = models.CharField(max_length=5, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return f"Title: {self.title}, Daily Fee: {self.daily_fee}"
