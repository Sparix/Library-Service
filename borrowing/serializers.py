from django.contrib.auth import get_user_model
from rest_framework import serializers
import datetime

from books.serializers import BookSerializerList
from borrowing.models import Borrowing


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
        )


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        date = super(BorrowingSerializer, self).validate(attrs)
        borrowing_date = datetime.date.today()
        if not (attrs["expected_return_date"] > borrowing_date):
            raise serializers.ValidationError(
                {"borrowing_date": "borrowing date can't be equal or earlier than expected return date"}
            )

        if attrs["actual_return_date"]:
            if not (attrs["actual_return_date"] >= borrowing_date):
                raise serializers.ValidationError(
                    {"borrowing_date": "borrowing date can't be earlier than actual return date"}
                )

        if not attrs["book"].inventory >= 1:
            raise serializers.ValidationError(
                {"inventory": "inventory must be greater than 0"}
            )

        return date

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        return Borrowing.objects.create(**validated_data)


class BorrowingListSerializer(BorrowingSerializer):
    book_title = serializers.SlugRelatedField(
        read_only=True,
        slug_field="title",
        source="book",
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book_title",
            "user",
        )


class BorrowingRetrieveSerializer(BorrowingListSerializer):
    book = BookSerializerList(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrowing_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
