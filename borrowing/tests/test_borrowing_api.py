import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status, test

from books.models import Authors, Genres, Books
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingListSerializer, BorrowingRetrieveSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_borrowing(borrowing_id: int):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def borrowing_return(borrowing_id: int):
    return reverse("borrowing:borrowing-borrowing-return", args=[borrowing_id])


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
        "expected_return_date": datetime.date.today() + datetime.timedelta(weeks=3),
        "book": book,
        "user": user,
    }
    default_borrowing.update(**params)
    return Borrowing.objects.create(**default_borrowing)


class UnAuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()
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
        serializers = BorrowingListSerializer(borrowing, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_borrowing_create_api(self):
        book = create_book()
        initial_inventory = book.inventory
        payload = {
            "expected_return_date": datetime.date.today() + datetime.timedelta(weeks=3),
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
        self.assertEqual(res.data, serializers.data)

    def test_filter_list_borrowing_api(self):
        book = create_book()

        create_borrowing(self.user, book, actual_return_date=datetime.date.today() + datetime.timedelta(days=2))
        create_borrowing(self.user, book, actual_return_date=datetime.date.today() + datetime.timedelta(weeks=3))
        create_borrowing(self.user, book)
        create_borrowing(self.user, book)

        res = self.client.get(BORROWING_URL, {"is_active": "True"})
        borrowing = Borrowing.objects.filter(actual_return_date=None)

        self.assertEqual(len(res.data), borrowing.count())

    def test_detail_borrowing_api(self):
        book = create_book()
        borrowing = create_borrowing(self.user, book)

        url = detail_borrowing(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingRetrieveSerializer(borrowing, many=False)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_borrowing_action_borrowing_return_book(self):
        book = create_book()
        borrowing = create_borrowing(self.user, book)
        instance_inventory = book.inventory
        url = borrowing_return(borrowing.id)
        res = self.client.put(url)
        book.refresh_from_db()
        borrowing.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, instance_inventory + 1)
        self.assertNotEqual(borrowing.actual_return_date, None)


class IsAdminBorrowingApi(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.com",
            password="test12345",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_borrowing_list_admin_api(self):
        new_user = get_user_model().objects.create_user(
            email="test@test.ua",
            password="test12345"
        )
        new_user1 = get_user_model().objects.create_user(
            email="user@user.ua",
            password="test12345"
        )
        book = create_book()

        create_borrowing(self.user, book)
        create_borrowing(new_user1, book)
        create_borrowing(new_user, book)

        res = self.client.get(BORROWING_URL)
        borrowing = Borrowing.objects.all()

        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), borrowing.count())

    def test_filter_user_borrowing_list_admin_api(self):
        test_user = get_user_model().objects.create_user(
            email="test@test.ua",
            password="test12345"
        )
        book = create_book()

        create_borrowing(self.user, book)
        create_borrowing(test_user, book)
        create_borrowing(test_user, book)

        res = self.client.get(BORROWING_URL, {"user_id": test_user.id})

        borrowing = Borrowing.objects.filter(user__id=test_user.id)
        serializer = BorrowingListSerializer(borrowing, many=True)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), borrowing.count())
