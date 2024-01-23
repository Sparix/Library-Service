from django.contrib.auth import get_user_model
from rest_framework import serializers

from books.serializers import BookSerializerList
from borrowing.models import Borrowing


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email",)


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "borrowing_date", "expected_return_date", "actual_return_date", "book", "user")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializerList(read_only=True)
    user = UserSerializer(read_only=True)
