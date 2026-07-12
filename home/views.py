from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .forms import EventForm
from .models import Event, Bookings


def home(request):
    events = Event.objects.filter(dnt__gte=timezone.now()).order_by('dnt')
    return render(request, 'home.html', {'events': events})


@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()

            messages.success(request, f"Event '{event.name}' created successfully!")
            return redirect("home")

        messages.error(request, "Please correct the errors below.")

    else:
        form = EventForm()

    return render(request, "event_form.html", {"form": form})


def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    bookings = event.bookings.select_related("participant").order_by("booked_at")

    user_has_joined = False
    my_seat_index = -1

    if request.user.is_authenticated:
        for index, booking in enumerate(bookings):
            if booking.participant == request.user:
                user_has_joined = True
                my_seat_index = index
                break

    context = {
        "event": event,
        "user_has_joined": user_has_joined,
        "my_seat_index": my_seat_index,
        "seat_range": range(event.total_seats),
        "attendees": bookings,
    }

    return render(request, "event_detail.html", context)


@login_required
def join_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if event.dnt < timezone.now():
        messages.error(request, "This event has already started.")
        return redirect("home")

    if request.method != "POST":
        return redirect("event_detail", event_id=event.id)

    if Bookings.objects.filter(event=event, participant=request.user).exists():
        messages.warning(request, "You've already joined this event.")

    elif event.seats <= 0:     # Make sure 'seats' exists in your model
        messages.error(request, "Sorry, this event is full.")

    else:
        Bookings.objects.create(
            event=event,
            participant=request.user
        )

        messages.success(request, f"Seat booked successfully for '{event.name}'.")

        if request.user.email:
            send_mail(
                subject=f"Booking Confirmed: {event.name}",
                message=(
                    f"Hi {request.user.username},\n\n"
                    f"Your booking for '{event.name}' has been confirmed.\n\n"
                    f"Date: {event.dnt.strftime('%b %d, %Y %I:%M %p')}\n"
                    f"Venue: {event.venue}\n\n"
                    f"See you there!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

    return redirect("event_detail", event_id=event.id)


@login_required
def cancel_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method != "POST":
        return redirect("event_detail", event_id=event.id)

    if event.organizer != request.user:
        messages.error(request, "You don't have permission to cancel this event.")
        return redirect("event_detail", event_id=event.id)

    emails = [
        booking.participant.email
        for booking in event.bookings.all()
        if booking.participant.email
    ]

    if emails:
        send_mail(
            subject=f"Event Cancelled: {event.name}",
            message=(
                f"Hi Participant,\n\n"
                f"The event '{event.name}' scheduled on "
                f"{event.dnt.strftime('%b %d, %Y %I:%M %p')} at "
                f"{event.venue} has been cancelled.\n\n"
                f"Please contact the organizer for more details."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )

    event_name = event.name
    event.delete()

    messages.success(request, f"Event '{event_name}' has been cancelled.")

    return redirect("home")


@login_required
def cancel_seat(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method != "POST":
        return redirect("event_detail", event_id=event.id)

    booking = Bookings.objects.filter(
        event=event,
        participant=request.user
    ).first()

    if booking:
        booking.delete()
        messages.success(request, "Your booking has been cancelled.")
    else:
        messages.warning(request, "You don't have a booking for this event.")

    return redirect("event_detail", event_id=event.id)


@login_required
def my_bookings(request):
    bookings = Bookings.objects.filter(
        participant=request.user
    ).select_related("event")

    return render(request, "my_bookings.html", {
        "bookings": bookings
    })


@login_required
def my_events(request):
    events = Event.objects.filter(
        organizer=request.user
    ).order_by("-dnt")

    return render(request, "my_events.html", {
        "events": events
    })