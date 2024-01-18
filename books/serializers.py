from rest_framework import serializers

from books.models import Book, Author, Genre


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "genre",
            "cover",
            "inventory",
            "daily_fee"
        )


class BookSerializerList(BookSerializer):
    author = serializers.CharField(source="genre__full_name", read_only=True)
    genre = GenreSerializer(read_only=True)