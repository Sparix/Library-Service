from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingListSerializer


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related(
        "book__author", "user"
    ).prefetch_related("book__genre")
    serializer_class = BorrowingSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer

        return self.serializer_class
