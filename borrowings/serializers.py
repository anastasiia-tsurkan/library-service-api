from django.db import transaction
from rest_framework import serializers

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return", "actual_return", "book", "user"]

    @transaction.atomic
    def create(self, validated_data):
        book_object = Book.objects.get(title=validated_data["book"])
        validated_data["user"] = self.context["request"].user
        if book_object.inventory > 0:
            book_object.inventory -= 1
            book_object.save()

            return super().create(validated_data)
        raise ValueError("This book is unavailable")


class BorrowingListSerializer(BorrowingSerializer):
    book = BookSerializer
    user = serializers.CharField(source="user.email")

    class Meta:
        model = Borrowing
        fields = "__all__"
