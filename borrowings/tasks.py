import asyncio
from datetime import datetime

from django.utils.timezone import now
from celery import shared_task

from borrowings.models import Borrowing
from borrowings.telegram_bot import send_notification_to_telegram


@shared_task
def send_msg_about_overdue_borrowings():
    overdue_borrowings = Borrowing.objects.filter(
        expected_return__lt=now().date()
    )
    if overdue_borrowings:
        for borrowing in overdue_borrowings:
            expected_return = datetime.strptime(
                str(borrowing.expected_return),
                "%Y-%m-%d"
            )
            asyncio.run(
                send_notification_to_telegram(msg=f"{borrowing.user.email} has an overdue "
                                                  f"book {borrowing.book.title}."
                                              f" Expected return was {expected_return}"
                                              )
            )
    else:
        asyncio.run(
            send_notification_to_telegram(msg="No overdue borrowings today")
        )
