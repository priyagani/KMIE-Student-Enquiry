import logging

from datetime import date
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Student, Enquiry, DemoBooking
from .forms import EnquiryForm, DemoBookingForm


logger = logging.getLogger(__name__)



def enquiry_create(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            mobile = data["mobile"]

            # Check whether this mobile number already exists.
            existing_student = Student.objects.filter(
                mobile=mobile
            ).first()

            if existing_student:
                messages.error(
                    request,
                    "This mobile number is already registered. "
                    "Please use a different number."
                )
                return render(
                    request,
                    "myapp/enquiry.html",
                    {"form": form}
                )

            try:
                with transaction.atomic():
                    student = Student.objects.create(
                        name=data["name"],
                        mobile=mobile,
                        email=data["email"],
                    )

                    enquiry = Enquiry.objects.create(
                        student=student,
                        student_class=data["student_class"],
                        course=data["course"],
                        source=data["source"],
                    )

                messages.success(
                    request,
                    "New student and enquiry registered successfully!"
                )

                return redirect(
                    "book_demo_with_enquiry",
                    enquiry_id=enquiry.pk
                )

            except IntegrityError:
                messages.error(
                    request,
                    "This mobile number may already be registered. "
                    "Please check and try again."
                )
    else:
        form = EnquiryForm()

    return render(
        request,
        "myapp/enquiry.html",
        {"form": form}
    )


def book_demo(request, enquiry_id):
    enquiry = get_object_or_404(
        Enquiry.objects.select_related("student"),
        pk=enquiry_id
    )

    if request.method == "POST":
        form = DemoBookingForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            # The submitted mobile must match the enquiry's student.
            if data["mobile"] != enquiry.student.mobile:
                form.add_error(
                    "mobile",
                    "This mobile number does not match the selected enquiry."
                )
            elif data["enquiry_id"] != enquiry.pk:
                form.add_error(
                    None,
                    "Invalid enquiry selected."
                )
            elif data["booking_date"] < date.today():
                form.add_error(
                    "booking_date",
                    "Please choose today or a future date."
                )
            else:
                try:
                    with transaction.atomic():
                        booking = DemoBooking.objects.create(
                            student=enquiry.student,
                            enquiry=enquiry,
                            booking_date=data["booking_date"],
                            booking_time=data["booking_time"],
                            status="Booked",
                            confirmation_message=(
                                "Mock confirmation: Demo booked for "
                                f"{enquiry.student.name} on "
                                f"{data['booking_date']} at "
                                f"{data['booking_time']}. "
                                "No real email was sent."
                            ),
                        )

                        enquiry.status = "Demo Booked"
                        enquiry.save(update_fields=["status"])

                        logger.info(
                            "MOCK DEMO CONFIRMATION | Student=%s | "
                            "Lead=%s | Date=%s | Time=%s",
                            enquiry.student.mobile,
                            enquiry.lead_id,
                            booking.booking_date,
                            booking.booking_time,
                        )

                    messages.success(
                        request,
                        "Demo booked successfully! "
                        "Mock confirmation was logged."
                    )
                    return redirect("dashboard")

                except IntegrityError:
                    messages.error(
                        request,
                        "This student has already booked that date "
                        "and time. Please select another slot."
                    )
    else:
        form = DemoBookingForm(
            initial={"enquiry_id": enquiry.pk}
        )

    return render(
        request,
        "myapp/booking.html",
        {
            "form": form,
            "enquiry": enquiry,
        }
    )


def dashboard(request):
    enquiries = Enquiry.objects.select_related("student").all()
    bookings = DemoBooking.objects.select_related(
        "student", "enquiry"
    ).all()

    # Filter enquiries by class and course.
    student_class = request.GET.get("student_class", "")
    course = request.GET.get("course", "")

    if student_class in {"11", "12"}:
        enquiries = enquiries.filter(student_class=student_class)

    if course in {"NEET Chemistry", "JEE Chemistry"}:
        enquiries = enquiries.filter(course=course)

    # Filter bookings by booking date and status.
    booking_date = request.GET.get("booking_date", "")
    status = request.GET.get("status", "")

    if booking_date:
        bookings = bookings.filter(booking_date=booking_date)

    if status in {"Booked", "Attended", "Cancelled"}:
        bookings = bookings.filter(status=status)

    total_enquiries = Enquiry.objects.count()
    unique_students = Student.objects.count()
    total_demos = DemoBooking.objects.count()
    attendance_count = DemoBooking.objects.filter(
        status="Attended"
    ).count()

    # Group all enquiries by student for the lead history.
    students = Student.objects.annotate(
        enquiry_count=Count("enquiries")
    ).order_by("-created_at")

    return render(
        request,
        "myapp/dashboard.html",
        {
            "enquiries": enquiries.order_by("-created_at"),
            "bookings": bookings,
            "students": students,
            "total_enquiries": total_enquiries,
            "unique_students": unique_students,
            "total_demos": total_demos,
            "attendance_count": attendance_count,
            "student_class": student_class,
            "course": course,
            "booking_date": booking_date,
            "status": status,
        }
    )


@require_POST
def update_booking_status(request, booking_id):
    booking = get_object_or_404(
        DemoBooking,
        pk=booking_id
    )

    new_status = request.POST.get("status", "")

    if new_status not in {"Booked", "Attended", "Cancelled"}:
        messages.error(request, "Invalid booking status.")
        return redirect("dashboard")

    booking.status = new_status
    booking.save(update_fields=["status"])

    messages.success(
        request,
        f"Demo status updated to {new_status}."
    )

    return redirect("dashboard")