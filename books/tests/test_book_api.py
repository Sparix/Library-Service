from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status, test

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
        self.client = test.APIClient()

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

    def test_update_detail_book(self):
        book = sample_book()
        genre = Genres.objects.create(name="Novel")
        url = detail_book(book.id)
        res = self.client.patch(
            url,
            book.genre.add(genre)
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_book(self):
        authors = author_create()

        book = sample_book(author=authors)
        genre = Genres.objects.create(name="Novel")
        book.genre.add(genre)
        url = detail_book(book.id)
        res = self.client.get(url)

        serializer = BookSerializerList(book)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_delete_book(self):
        authors = author_create()

        book = sample_book(author=authors)

        url = detail_book(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTest(UnauthenticatedBookApiTest):
    def setUp(self):
        self.client = test.APIClient()

        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_update_detail_book(self):
        book = sample_book()
        genre = Genres.objects.create(name="Novel")
        url = detail_book(book.id)
        res = self.client.patch(
            url,
            book.genre.add(genre)
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book(self):
        authors = author_create()

        book = sample_book(author=authors)

        url = detail_book(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class IsAdminUserBookApiTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()

        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="test12345",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_book(self):
        sample_book()
        authors = author_create()
        sample_book(author=authors)
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
        authors = author_create()
        genre = Genres.objects.create(name="Novel")
        genre1 = Genres.objects.create(name="TestGenre")
        payload = {
            "title": "test_book",
            "author": authors.id,
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

    def test_detail_book_update(self):
        book = sample_book()
        genre = Genres.objects.create(name="Novel")
        url = detail_book(book.id)
        res = self.client.patch(
            url,
            book.genre.add(genre)
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_detail_book_delete(self):
        book = sample_book()
        url = detail_book(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
