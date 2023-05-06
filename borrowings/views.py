import datetime

from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer


# class BorrowingListView(
#     viewsets.ModelViewSet
# ):
#     serializer_class = BorrowingSerializer
#     permission_classes = ("IsAdmin",)
#     queryset = Borrowing.objects.select_related("user", "book")


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
        queryset = self.queryset
        user_id = self.request.query_params.get("user_id")
        is_active = self.request.query_params.get("is_active")

        if user_id:
            queryset = self.queryset.filter(user__id=user_id)

        if is_active is True:
            queryset = self.queryset.filter(actual_return__isnull=True)
        if is_active is False:
            queryset = self.queryset.filter(actual_return__isnull=False)

        if user.is_staff:
            return queryset

        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
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
