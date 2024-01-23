from django.conf import settings
from django.db import models

from books.models import Books


class Borrowing(models.Model):
    borrowing_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True, default=None)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="borrowing_book")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowing_user")

    def __str__(self) -> str:
        return f"{self.borrowing_date} - {self.book.title}"
