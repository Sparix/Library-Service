from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


SOFT, HARD = "soft", "hard"
COVER = (
    (SOFT, "SOFT"),
    (HARD, "HARD"),
)


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        related_name="books_author",
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True
    )
    cover = models.CharField(max_length=5, choices=COVER)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=2, max_digits=5)

    def __str__(self):
        return f"Title: {self.title}, Daily Fee: {self.daily_fee}"
