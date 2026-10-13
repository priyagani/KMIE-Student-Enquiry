from django.contrib import admin

from .models import Student, Enquiry, DemoBooking


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "email", "created_at")
    search_fields = ("name", "mobile", "email")


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "lead_id",
        "student",
        "student_class",
        "course",
        "source",
        "status",
        "created_at",
    )
    list_filter = ("student_class", "course", "source", "status")
    search_fields = ("student__name", "student__mobile", "lead_id")


@admin.register(DemoBooking)
class DemoBookingAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "booking_date",
        "booking_time",
        "status",
    )
    list_filter = ("booking_date", "booking_time", "status")
    search_fields = ("student__name", "student__mobile")