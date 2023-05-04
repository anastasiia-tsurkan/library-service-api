from rest_framework import serializers

from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "borrow_date", "expected_return", "actual_return", "book", "user"]
