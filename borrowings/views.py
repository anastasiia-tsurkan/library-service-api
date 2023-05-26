from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin
):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            self.queryset = self.queryset.filter(user__id=user_id)

        if is_active == "true":
            self.queryset = self.queryset.filter(actual_return__isnull=True)
        if is_active == "false":
            self.queryset = self.queryset.filter(actual_return__isnull=False)
        if user.is_staff:
            return self.queryset

        return self.queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    @transaction.atomic()
    @action(methods=["POST"], detail=True, url_path="return", serializer_class=None)
    def return_borrowing(self, request, pk):
        borrowing = self.get_object()
        if borrowing.actual_return is not None:
            raise ValueError("You cannot return borrowing twice")
        if borrowing.user != self.request.user:
            raise ValueError("You can`t return borrowing")

        borrowing.actual_return = timezone.now()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response(
            {"status": "This borrowing is closed successfully"},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by actual active borrowings",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter borrowings by user id",
                required=False,
                type=int,
            )
        ]
    )
    def list(self, request, *args, **kwargs):  # -> Response:
        return super().list(request, *args, **kwargs)
