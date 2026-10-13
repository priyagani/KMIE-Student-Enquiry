from django import forms
from django.core.validators import RegexValidator

from .models import Enquiry, DemoBooking


class EnquiryForm(forms.Form):
    name = forms.CharField(max_length=100)
    mobile = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[6-9]\d{9}$",
                message="Enter a valid 10-digit Indian mobile number."
            )
        ]
    )
    email = forms.EmailField()
    student_class = forms.ChoiceField(
    choices=[("", "-- Select Student Class --")] + list(Enquiry.CLASS_CHOICES),
    initial="",
    required=True,
    widget=forms.Select(attrs={
        "id": "id_student_class"
    })
)
    course = forms.ChoiceField(
    choices=[("", "-- Select Course --")] + list(Enquiry.COURSE_CHOICES),
    initial="",
    required=True,
    widget=forms.Select(attrs={
        "id": "id_course"
    })
)


class DemoBookingForm(forms.Form):
    mobile = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[6-9]\d{9}$",
                message="Enter a valid 10-digit Indian mobile number."
            )
        ]
    )

    enquiry_id = forms.IntegerField(
        widget=forms.HiddenInput()
    )

    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"})
    )

    booking_time = forms.ChoiceField(
        choices=DemoBooking.TIME_CHOICES
    )