from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request, "home.html")

def send_test_email(request):
    send_mail(
        subject="Test Email",
        message="This is a test email from Django.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["your_email@example.com"],  # Replace with your email
        fail_silently=False,
    )
    return HttpResponse("Email sent successfully!")