from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingRetrieveSerializer, BorrowingReturnSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related(
        "book__author", "user"
    ).prefetch_related("book__genre")
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer

        if self.action == "retrieve":
            return BorrowingRetrieveSerializer

        if self.action == "borrowing_return":
            return BorrowingReturnSerializer

        return self.serializer_class

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if is_active:
            queryset = queryset.filter(actual_return_date=None)

        if self.request.user.is_staff:
            if user_id:
                queryset = queryset.filter(user__id=user_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["put"])
    def borrowing_return(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnSerializer(borrowing, data=request.data)
        if borrowing.actual_return_date is None:
            if serializer.is_valid():
                serializer.update(borrowing, serializer.validated_data)

                return Response({
                    "actual_return_date": "You have returned the book"
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"actual_return_date": "You have already returned this book"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=str,
                description="Filter by non returned borrowing book"
            ),
            OpenApiParameter(
                "user_id",
                type={"type": "number"},
                description=(
                        "Filter borrowing records "
                        "based on a specific user, "
                        "applicable for administrators."
                )
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
