from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.urls import reverse_lazy
from events.models import Event
from django.contrib.auth.models import User


# ✅ Home Page
def home(request):
    return render(request, 'events/home.html')


# ✅ List Events with Search
def event_list(request):
    query = request.GET.get('q')
    events = Event.objects.filter(
        Q(name__icontains=query) | Q(location__icontains=query)) if query else Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


# ✅ Event Details
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


def contact(request):
    return render(request,
                  'events/contact.html')