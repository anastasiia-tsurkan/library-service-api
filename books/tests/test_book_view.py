from _decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def sample_book(**params):
    defaults = {
        "title": "Test title",
        "author": "Test author",
        "cover": "Soft",
        "inventory": 1,
        "daily_fee": 1.99,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_retrieve_allow_any(self):
        sample_book()
        sample_book(title="Test book 2")

        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_allow_any(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_movie_forbidden(self):
        payload = {
            "title": "Book test",
            "author": "Test author",
            "cover": "Hard",
            "inventory": 2,
            "daily_fee": 1.99
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "test12345"
        )
        self.client.force_authenticate(self.user)

    def test_delete_book_forbidden(self):
        book = sample_book()

        res = self.client.delete(detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "test12345",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Book test",
            "author": "Test author",
            "cover": "Hard",
            "inventory": 2,
            "daily_fee": Decimal("1.99"),
        }

        res = self.client.post(BOOK_URL, payload)
        book = Book.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self):
        book = sample_book()

        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
