import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Authors, Genres, Books
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")


def create_book():
    author = Authors.objects.create(first_name="Test", last_name="Testovich")
    genre = Genres.objects.create(name="Test")
    book = Books.objects.create(
        title="TestBook",
        author=author,
        inventory=2,
        daily_fee=1.9,
        cover="soft",
    )
    book.genre.add(genre)
    return book


def create_borrowing(user, book, **params):
    default_borrowing = {
        "expected_return_date": f"2024-02-{random.randint(1, 10)}",
        "book": book,
        "user": user,
    }
    default_borrowing.update(**params)
    return Borrowing.objects.create(**default_borrowing)


class UnAuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.com",
            password="test12345",
        )
        self.client.force_authenticate(self.user)

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_borrowing_list_api(self):
        book = create_book()
        create_borrowing(self.user, book)
        create_borrowing(self.user, book)
        res = self.client.get(BORROWING_URL)
        borrowing = Borrowing.objects.all()
        sorted_res_data = sorted(res.data, key=lambda x: x['id'])
        serializers = BorrowingListSerializer(borrowing, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted_res_data, serializers.data)

    def test_borrowing_create_api(self):
        book = create_book()
        initial_inventory = book.inventory
        payload = {
            "expected_return_date": f"2024-02-{random.randint(1, 10)}",
            "actual_return_date": "",
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, payload)
        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(book.inventory, initial_inventory - 1)

    def test_borrowing_list_for_current_user(self):
        new_user = get_user_model().objects.create_user(
            email="test@test.ua",
            password="test12345"
        )
        book = create_book()

        create_borrowing(self.user, book)
        create_borrowing(self.user, book)
        create_borrowing(new_user, book)

        res = self.client.get(BORROWING_URL)
        borrowing_list = Borrowing.objects.filter(user=self.user)

        serializers = BorrowingListSerializer(borrowing_list, many=True)

        self.assertEqual(len(res.data), len(serializers.data))

    def test_filter_list_borrowing_api(self):
        book = create_book()

        create_borrowing(self.user, book, actual_return_date="2024-01-28")
        create_borrowing(self.user, book, actual_return_date="2024-02-01")
        create_borrowing(self.user, book)
        create_borrowing(self.user, book)

        res = self.client.get(BORROWING_URL, {"is_active": "True"})
        borrowing = Borrowing.objects.filter(actual_return_date=None)

        self.assertEqual(len(res.data), borrowing.count())
