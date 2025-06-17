import random
import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.models import User
from .models import Booking  # adjust this import as per your Booking model
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from .models import Booking, Event


# ✅ User Signup with OTP
def user_signup(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        # ✅ Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'users/signup.html', {'username': username, 'email': email, 'phone': phone})

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'users/signup.html', {'username': username, 'email': email, 'phone': phone})

        # ✅ Generate OTP & Set Expiry Time (5 mins)
        otp = str(random.randint(1000, 9999))
        request.session['otp'] = otp
        request.session['otp_expiry'] = (datetime.datetime.now() + datetime.timedelta(minutes=5)).timestamp()
        request.session['signup_data'] = {
            'username': username,
            'email': email,
            'phone': phone,
            'password': password,
        }

        # ✅ Send OTP via email
        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}. It expires in 5 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "OTP sent to your email!")
        except Exception as e:
            messages.error(request, "Error sending OTP. Try again.")
            return render(request, 'users/signup.html', {'username': username, 'email': email, 'phone': phone})

        return redirect('users:verify_otp')  # ✅ Fixed namespace issue

    return render(request, 'users/signup.html')


# ✅ OTP Verification
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp", "").strip()
        correct_otp = request.session.get("otp")
        otp_expiry = request.session.get("otp_expiry")
        signup_data = request.session.get("signup_data")  # Get stored data

        if not signup_data:
            messages.error(request, "Session expired. Please sign up again.")
            return redirect("users:signup")

        if not correct_otp or not otp_expiry or datetime.datetime.now().timestamp() > otp_expiry:
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect("users:send_otp")

        if entered_otp == correct_otp:
            # ✅ Retrieve correct user data
            username = signup_data["username"]
            email = signup_data["email"]
            phone = signup_data["phone"]
            password = signup_data["password"]

            # ✅ Create user if not exists
            user, created = User.objects.get_or_create(username=username, email=email)
            if created:
                user.set_password(password)  # Set the actual password
                user.save()

            # ✅ Log in the user immediately after OTP verification
            login(request, user)
            messages.success(request, "Signup successful! You are now logged in.")

            # ✅ Clear session after success
            request.session.pop("otp", None)
            request.session.pop("otp_expiry", None)
            request.session.pop("signup_data", None)

            return redirect("events:home")  # Redirect to your homepage
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, "users/verify_otp.html")


# ✅ User Login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username', '')  # Default to empty string if None
        password = request.POST.get('password', '')  # Default to empty string if None

        username = username.strip()  # Avoid AttributeError
        password = password.strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'users/login.html')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('events:home')  # Change 'home' to your actual homepage URL
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'users/login.html')


# ✅ User Logout
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('users:login')


def send_otp(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Please enter a valid email.")
            return redirect("users:send_otp")

        # ✅ Generate OTP and set expiry time
        otp = str(random.randint(100000, 999999))
        otp_expiry = datetime.datetime.now().timestamp() + 300  # 5 mins expiry

        # ✅ Store OTP and email in session
        request.session["otp"] = otp
        request.session["otp_expiry"] = otp_expiry
        request.session["email"] = email  # Store email correctly

        # ✅ Send OTP via email
        send_mail(
            "Your OTP Code",
            f"Your OTP code is: {otp}. It is valid for 5 minutes.",
            "your_email@example.com",  # Change to your sender email
            [email],
            fail_silently=False,
        )

        messages.success(request, "OTP sent successfully. Check your email.")
        return redirect("users:verify_otp")

    return render(request, "users/send_otp.html")


# ✅ Admin Signup
def admin_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            return render(request, 'users/admin_signup.html', {'error': 'Username already exists'})

        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True  # ✅ Set is_staff separately
        user.save()

        return redirect('users:admin_login')  # ✅ Fixed redirect with namespace

    return render(request, 'users/admin_signup.html')


# ✅ Admin Login
def admin_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Only allow staff (admin) users
            login(request, user)
            return redirect("users:admin_dashboard")  # Redirect to admin dashboard
        else:
            return render(request, "users/admin_login.html", {"error": "Invalid credentials or not an admin"})

    return render(request, "users/admin_login.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from events.models import Event
from users.models import Booking
from .forms import EventForm, EditProfileForm


@login_required(login_url='users:login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("users:login")

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('users:admin_dashboard')

    else:
        form = EventForm()

    context = {
        "total_bookings": Booking.objects.count(),
        "total_live_events": Event.objects.count(),
        "events": Event.objects.all(),
        "event_form": form
    }

    return render(request, "users/admin_dashboard.html", context)


# ✅ Edit Performance
from django.shortcuts import get_object_or_404, render, redirect
from events.models import Event
from .forms import EventForm


def edit_event(request, id):
    event = get_object_or_404(Event, id=id)
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect("users:admin_dashboard")  # Update URL name if needed
    else:
        form = EventForm(instance=event)

    return render(request, "users/edit_event.html", {"form": form})


def delete_event(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect("users:admin_dashboard")


# ✅ Admin Logout
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'email', 'members', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'members': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any special requests?', 'rows': 3}),
        }


from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking
from .forms import BookingForm
from events.models import Event
from django.core.mail import send_mail
from django.conf import settings


def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.event = event
            booking.user = request.user
            booking.save()

            # Send confirmation email
            subject = f"Booking Confirmation for {event.name}"
            message = f"Hi {booking.name},\n\nYou have successfully booked {booking.members} ticket(s) for the event \"{event.name}\" on {event.date} at {event.time}.\n\nLocation: {event.location}\n\nThank you for booking with us!"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.email])

            return redirect('users:booking_success')
    else:
        form = BookingForm()

    return render(request, 'users/book_event.html', {'form': form, 'event': event})


from django.shortcuts import render


def booking_success(request):
    return render(request, 'users/booking_success.html')


from datetime import timedelta
from django.utils import timezone


@login_required
def profile_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-event__date')

    now = timezone.now()

    upcoming = bookings.filter(event__date__range=[now, now + timedelta(days=1)])

    saved_events = request.user.saved_events.all() if hasattr(request.user, 'saved_events') else []

    return render(request, 'users/profile.html', {
        'bookings': bookings,
        'upcoming': upcoming,
        'saved_events': saved_events
    })


from django.contrib.auth.forms import UserChangeForm


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Event


@login_required
def toggle_save_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.user in event.saved_by.all():
        event.saved_by.remove(request.user)
        action = "removed"
    else:
        event.saved_by.add(request.user)
        action = "saved"

    return JsonResponse({'status': 'ok', 'action': action})
