from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books.models import Books, Authors, Genres
from books.serializers import BookSerializerList

BOOK_URL = reverse("books:books-list")


def detail_book(books_id: int):
    return reverse("books:books-detail", args=[books_id])


def sample_book(**params):
    default_book = {
        "title": "TestBook",
        "inventory": 1,
        "daily_fee": 1.9,
        "cover": "SOFT"
    }
    default_book.update(**params)
    return Books.objects.create(**default_book)


def author_create():
    return Authors.objects.create(first_name="Test", last_name="Testovich")


class UnauthenticatedBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_book(self):
        sample_book()
        author = author_create()
        sample_book(author=author)
        genre = Genres.objects.create(name="Novel")
        genre1 = Genres.objects.create(name="TestGenre")
        book_with_genre = sample_book()
        book_with_genre.genre.add(genre, genre1)
        res = self.client.get(BOOK_URL)
        books = Books.objects.all()

        serializer = BookSerializerList(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book(self):
        author = author_create()
        genre = Genres.objects.create(name="Humor")
        genre1 = Genres.objects.create(name="test")
        payload = {
            "title": "test_book",
            "author": author.id,
            "genre": [genre1.id, genre.id],
            "inventory": 1,
            "daily_fee": 1.9,
            "cover": "soft"
        }

        res = self.client.post(BOOK_URL, payload)
        book = Books.objects.get(id=res.data["id"])
        genres = book.genre.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(genres.count(), 2)
        self.assertIn(genre, genres)
        self.assertIn(genre1, genres)

    def test_create_book_without_genre(self):
        authors = author_create()
        payload = {
            "title": "test_book",
            "author": authors.id,
            "inventory": 1,
            "daily_fee": 1.9,
            "cover": "soft"
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
