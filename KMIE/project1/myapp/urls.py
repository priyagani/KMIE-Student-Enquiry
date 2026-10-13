from django.urls import path

from . import views

urlpatterns = [
    path("", views.enquiry_create, name="enquiry_create"),

    path(
        "book-demo/<int:enquiry_id>/",
        views.book_demo,
        name="book_demo_with_enquiry",
    ),

    path("dashboard/", views.dashboard, name="dashboard"),

    path(
        "booking/<int:booking_id>/status/",
        views.update_booking_status,
        name="update_booking_status",
    ),
]