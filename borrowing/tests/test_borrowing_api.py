from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

BORROWING_URL = reverse("borrowing:borrowing-list")


class UnAuthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
