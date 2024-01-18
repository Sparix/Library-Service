from rest_framework import serializers

from books.models import Books, Authors, Genres


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ("id", "name")


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
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
