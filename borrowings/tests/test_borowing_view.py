from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from books.tests.test_book_view import sample_book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingListSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def return_url(borrowing_id):
    return reverse(
        "borrowings:borrowing-return-borrowing",
        args=[borrowing_id]
    )


def sample_user(email: str, **params):
    defaults = {
        "email": email,
        "password": "test12345",
        "first_name": "Test name",
        "last_name": "Test surname",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_borrowing(user: get_user_model(), **params):
    book = sample_book()
    defaults = {
        "expected_return": date(2060, 1, 1),
        "book": book,
        "user": user
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = sample_user(email="test1@test.com")
        sample_borrowing(user=user)

    def test_list_(self):
        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@test.com",
            "test12345"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_only_users_borrowings(self):
        other_user = sample_user(email="user3@user.com")
        sample_borrowing(user=other_user)
        book = sample_book(title="Test book 2")
        sample_borrowing(user=self.user, book=book)

        res = self.client.get(BORROWING_URL)
        users_borrowings = Borrowing.objects.filter(user=self.user.id)
        serializer_user = BorrowingListSerializer(users_borrowings, many=True)

        all_borrowings = Borrowing.objects.all()
        serializer_all = BorrowingListSerializer(all_borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer_user.data)
        self.assertNotEqual(res.data, serializer_all.data)

    def test_create_new_borrowing_successful(self):
        book = sample_book()
        inventory_before = book.inventory
        payload = {
            "expected_return": date(2060, 1, 1),
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, payload)
        borrowing = Borrowing.objects.get(id=res.data["id"])
        inventory_after = borrowing.book.inventory

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(inventory_after, inventory_before - 1)

    def test_return_borrowing_successful(self):
        book = sample_book()
        inventory_before = book.inventory
        user_borrowing = sample_borrowing(user=self.user, book=book)

        url = return_url(user_borrowing.id)
        res = self.client.post(url)
        inventory_after = user_borrowing.book.inventory

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_borrowing.refresh_from_db()
        self.assertIsNotNone(user_borrowing.actual_return)
        self.assertEqual(inventory_after, inventory_before)
        self.assertEqual(
            res.data,
            {"status": "This borrowing is closed successfully"}
        )

    def test_return_borrowing_twice_forbidden(self):
        borrowing = sample_borrowing(user=self.user, book=sample_book())
        url = return_url(borrowing.id)
        borrowing.actual_return = timezone.now().date()
        borrowing.save()

        with self.assertRaises(ValueError):
            self.client.post(url)

    def test_return_others_user_borrowing_not_found(self):
        other_user = sample_user(email="other@user.com")
        other_borrowing = sample_borrowing(user=other_user, book=sample_book())
        url = return_url(other_borrowing.id)

        res = self.client.post(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "test12345",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_filtering_with_is_active_param(self):
        book1 = sample_book(title="Book 1")
        user1 = sample_user(email="user1@test.com")

        sample_borrowing(user=user1, book=book1)
        borrowings_active = Borrowing.objects.filter(
            actual_return__isnull=True
        )
        serializer_active = BorrowingListSerializer(
            borrowings_active,
            many=True
        )

        borrowing_not_active = sample_borrowing(user=user1, book=book1)
        borrowing_not_active.actual_return = date(2024, 1, 1)
        borrowing_not_active.save()
        borrowings_not_active = Borrowing.objects.filter(
            actual_return__isnull=False
        )
        serializer_not_active = BorrowingListSerializer(
            borrowings_not_active,
            many=True
        )

        url_active = BORROWING_URL + "?is_active=true"
        url_not_active = BORROWING_URL + "?is_active=false"

        res_is_active = self.client.get(url_active)

        res_is_not_active = self.client.get(url_not_active)

        self.assertEqual(res_is_active.data, serializer_active.data)
        self.assertEqual(res_is_not_active.data, serializer_not_active.data)

    def test_filtering_with_user_id_param(self):
        book1 = sample_book(title="Book 1")

        user1 = sample_user(email="user1@test.com")
        user2 = sample_user(email="user2@test.com")

        sample_borrowing(user=user1, book=book1)
        borrowings_1 = Borrowing.objects.filter(user__id=user1.id)
        serializer_1 = BorrowingListSerializer(borrowings_1, many=True)

        sample_borrowing(user=user2, book=book1)
        borrowings_2 = Borrowing.objects.filter(user__id=user2.id)
        serializer_2 = BorrowingListSerializer(borrowings_2, many=True)

        url_1 = BORROWING_URL + f"?user_id={user1.id}"
        url_2 = BORROWING_URL + f"?user_id={user2.id}"

        res_1 = self.client.get(url_1)

        res_2 = self.client.get(url_2)

        self.assertEqual(res_1.data, serializer_1.data)
        self.assertEqual(res_2.data, serializer_2.data)
        self.assertNotEqual(res_1.data, serializer_2.data)
