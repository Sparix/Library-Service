from rest_framework import viewsets

from books.models import Books
from books.serializers import BookSerializer, BookSerializerList


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.prefetch_related(
        "genre"
    ).select_related(
        "author"
    )
    serializer_class = BookSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return BookSerializerList
        return BookSerializer
