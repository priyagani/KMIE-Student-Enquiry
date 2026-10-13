import uuid

from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


mobile_validator = RegexValidator(
    regex=r"^[6-9]\d{9}$",
    message="Enter a valid 10-digit Indian mobile number."
)


class Student(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(
        max_length=10,
        unique=True,
        validators=[mobile_validator]
    )
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"


class Enquiry(models.Model):
    CLASS_CHOICES = [
        ("11", "Class 11"),
        ("12", "Class 12"),
    ]

    COURSE_CHOICES = [
        ("NEET Chemistry", "NEET Chemistry"),
        ("JEE Chemistry", "JEE Chemistry"),
    ]

    SOURCE_CHOICES = [
        ("Website", "Website"),
        ("Walk-in", "Walk-in"),
        ("Phone", "Phone"),
        ("Referral", "Referral"),
        ("Social Media", "Social Media"),
    ]

    STATUS_CHOICES = [
        ("New", "New"),
        ("Contacted", "Contacted"),
        ("Demo Booked", "Demo Booked"),
        ("Converted", "Converted"),
        ("Closed", "Closed"),
    ]

    lead_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="enquiries"
    )

    student_class = models.CharField(
        max_length=2,
        choices=CLASS_CHOICES
    )

    course = models.CharField(
        max_length=30,
        choices=COURSE_CHOICES
    )

    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="New"
    )

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{str(self.lead_id)[:8]} - {self.student.name}"


class DemoBooking(models.Model):
    TIME_CHOICES = [
        ("13:00", "1:00 PM"),
        ("15:00", "3:00 PM"),
        ("17:00", "5:00 PM"),
        ("19:00", "7:00 PM"),
    ]

    STATUS_CHOICES = [
        ("Booked", "Booked"),
        ("Attended", "Attended"),
        ("Cancelled", "Cancelled"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="demo_bookings"
    )

    enquiry = models.ForeignKey(
        Enquiry,
        on_delete=models.PROTECT,
        related_name="demo_bookings"
    )

    booking_date = models.DateField()
    booking_time = models.CharField(
        max_length=5,
        choices=TIME_CHOICES
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Booked"
    )

    confirmation_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "booking_date",
                    "booking_time"
                ],
                name="unique_student_demo_slot"
            )
        ]
        ordering = ["booking_date", "booking_time"]

    def __str__(self):
        return (
            f"{self.student.name} - "
            f"{self.booking_date} - {self.booking_time}"
        )