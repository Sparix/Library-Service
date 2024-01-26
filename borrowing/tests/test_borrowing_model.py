from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from books.models import Books, Authors, Genres
from borrowing.models import Borrowing


def create_book():
    author = Authors.objects.create(first_name="Test", last_name="Testovich")
    genre = Genres.objects.create(name="Test")
    book = Books.objects.create(
        title="TestBook",
        author=author,
        inventory=1,
        daily_fee=1.9,
        cover="soft",
    )
    book.genre.add(genre)
    return book


def create_user():
    return get_user_model().objects.create_user(
        email="user@user.com",
        password="test12345",
    )


class TestBorrowingModel(TestCase):
    def test_borrowing_str(self):
        borrowing = Borrowing.objects.create(
            expected_return_date="2024-02-26",
            book=create_book(),
            user=create_user(),
        )

        self.assertEqual(
            str(borrowing),
            f"{borrowing.borrowing_date} - {borrowing.book.title}"
        )

    def test_borrowing_constrains_expected_return_date(self):
        book = create_book()
        user = create_user()

        with self.assertRaises(IntegrityError) as raised_1:
            with transaction.atomic():
                Borrowing.objects.create(
                    borrowing_date="2024-01-26",
                    expected_return_date="2024-01-26",
                    book=book,
                    user=user,
                )

        with self.assertRaises(IntegrityError) as raised_2:
            with transaction.atomic():
                Borrowing.objects.create(
                    borrowing_date="2024-01-26",
                    expected_return_date="2024-01-20",
                    book=book,
                    user=user,
                )

        borrowing_1 = Borrowing.objects.create(
            borrowing_date="2024-01-26",
            expected_return_date="2024-01-27",
            book=book,
            user=user,
        )

        self.assertEqual(IntegrityError, type(raised_1.exception))
        self.assertEqual(IntegrityError, type(raised_2.exception))
        self.assertEqual(str(borrowing_1.borrowing_date), "2024-01-26")
        self.assertEqual(str(borrowing_1.expected_return_date), "2024-01-27")

    def test_borrowing_constrains_actual_return_date(self):
        book = create_book()
        user = create_user()
        with self.assertRaises(IntegrityError) as raised_1:
            with transaction.atomic():
                Borrowing.objects.create(
                    borrowing_date="2024-01-26",
                    expected_return_date="2024-01-28",
                    actual_return_date="2024-01-24",
                    book=book,
                    user=user,
                )

        borrowing_1 = Borrowing.objects.create(
            borrowing_date="2024-01-26",
            expected_return_date="2024-01-28",
            actual_return_date="2024-01-26",
            book=book,
            user=user,
        )

        self.assertEqual(IntegrityError, type(raised_1.exception))
        self.assertEqual(str(borrowing_1.actual_return_date), "2024-01-26")
