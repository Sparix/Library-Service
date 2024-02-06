from django.core.exceptions import ValidationError
from django.test import TestCase

from books.models import Authors, Genres, Books


class ModelsBookTest(TestCase):
    def test_book_str(self):
        book = Books.objects.create(
            title="TestBook",
            inventory=1,
            daily_fee=1.9,
        )
        self.assertEqual(
            str(book),
            f"Title: {book.title}, "
            f"Daily Fee: {book.daily_fee}"
        )

    def test_author_and_genre_str(self):
        author = Authors.objects.create(first_name="Test", last_name="Testovich")
        genre = Genres.objects.create(name="TestGenre")

        self.assertEqual(str(author), f"{author.first_name} {author.last_name}")
        self.assertEqual(author.full_name, f"{author.first_name} {author.last_name}")
        self.assertEqual(str(genre), genre.name)
