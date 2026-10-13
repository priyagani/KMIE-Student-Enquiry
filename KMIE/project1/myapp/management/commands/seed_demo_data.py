from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from myapp.models import Student, Enquiry, DemoBooking


class Command(BaseCommand):
    help = "Create five fictional KMIE test students and demo bookings"

    def handle(self, *args, **options):
        today = timezone.localdate()

        test_records = [
            {
                "name": "Aarav Test",
                "mobile": "9000000001",
                "email": "aarav.test@example.com",
                "student_class": "11",
                "course": "NEET Chemistry",
                "source": "Website",
            },
            {
                "name": "Diya Sample",
                "mobile": "9000000002",
                "email": "diya.sample@example.com",
                "student_class": "12",
                "course": "JEE Chemistry",
                "source": "Referral",
            },
            {
                "name": "Rohan Demo",
                "mobile": "9000000003",
                "email": "rohan.demo@example.com",
                "student_class": "11",
                "course": "JEE Chemistry",
                "source": "Walk-in",
            },
            {
                "name": "Meera Sample",
                "mobile": "9000000004",
                "email": "meera.sample@example.com",
                "student_class": "12",
                "course": "NEET Chemistry",
                "source": "Social Media",
            },
            {
                "name": "Kabir Test",
                "mobile": "9000000005",
                "email": "kabir.test@example.com",
                "student_class": "11",
                "course": "NEET Chemistry",
                "source": "Phone",
            },
        ]

        for index, record in enumerate(test_records):
            student, _ = Student.objects.update_or_create(
                mobile=record["mobile"],
                defaults={
                    "name": record["name"],
                    "email": record["email"],
                },
            )

            enquiry, _ = Enquiry.objects.get_or_create(
                student=student,
                student_class=record["student_class"],
                course=record["course"],
                source=record["source"],
            )

            # Create three sample bookings.
            if index < 3:
                booking_date = today + timedelta(days=index + 1)
                booking_time = ["13:00", "15:00", "17:00"][index]

                booking, created = DemoBooking.objects.get_or_create(
                    student=student,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    defaults={
                        "enquiry": enquiry,
                        "status": (
                            "Attended" if index == 0 else "Booked"
                        ),
                        "confirmation_message": (
                            "MOCK CONFIRMATION: Fictional test booking."
                        ),
                    },
                )

                if created:
                    self.stdout.write(
                        f"Created demo booking for {student.name}"
                    )

            self.stdout.write(
                f"Ready: {student.name} | {enquiry.course}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Five fictional test students are ready."
            )
        )