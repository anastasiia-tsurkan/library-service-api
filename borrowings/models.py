from django.contrib.auth import get_user_model
from django.db import models

from books.models import Book
from users.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return = models.DateField()
    actual_return = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.user.email}: {self.book.title} -> {self.expected_return}"
