"""
EMS Views — Full feature set:
Auth, Dashboard, Events, Registrations, Analytics, Profile, Admin
"""
import csv
import json
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Profile, Event, Registration
from .forms import RegisterForm, LoginForm, EventForm, ProfileForm, UserRoleForm
from .decorators import role_required

from django.core.mail import send_mail
from django.conf import settings
from .signals import _send_confirmation_email

# ══════════════════════════════════════════════
# AUTH VIEWS
# ══════════════════════════════════════════════

def home(request):
    """Public landing page with featured events."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    events = Event.objects.filter(
        status='published', date__gte=timezone.now()
    ).order_by('date')[:6]
    return render(request, 'ems/home.html', {'events': events})


def register_view(request):
    """User self-registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('dashboard')
        messages.error(request, "Please fix the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'ems/auth/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'ems/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You've been logged out.")
    return redirect('login')


# ══════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════

@login_required
def dashboard(request):
    """Role-based dashboard view."""
    role = request.user.profile.role
    context = {'role': role}

    if role == 'admin':
        context.update({
            'total_users': User.objects.count(),
            'total_events': Event.objects.count(),
            'total_registrations': Registration.objects.count(),
            'published_events': Event.objects.filter(status='published').count(),
            'recent_registrations': Registration.objects.select_related(
                'user', 'event'
            ).order_by('-registered_at')[:10],
            'upcoming_events': Event.objects.filter(
                status='published', date__gte=timezone.now()
            ).order_by('date')[:5],
        })

    elif role == 'manager':
        my_events = Event.objects.filter(created_by=request.user)
        context.update({
            'my_events': my_events.order_by('-created_at')[:5],
            'total_my_events': my_events.count(),
            'total_registrations': Registration.objects.filter(
                event__created_by=request.user
            ).count(),
            'upcoming_events': my_events.filter(
                status='published', date__gte=timezone.now()
            ).order_by('date')[:5],
        })

    else:  # attendee
        my_regs = Registration.objects.filter(
            user=request.user
        ).select_related('event').order_by('-registered_at')
        context.update({
            'my_registrations': my_regs[:5],
            'total_registrations': my_regs.count(),
            'upcoming_events': Event.objects.filter(
                status='published', date__gte=timezone.now()
            ).order_by('date')[:6],
        })

    return render(request, 'ems/dashboard.html', context)


# ══════════════════════════════════════════════
# EVENT VIEWS
# ══════════════════════════════════════════════

def event_list(request):
    """Public event listing with search/filter."""
    events = Event.objects.filter(status='published', date__gte=timezone.now())

    # Search
    query = request.GET.get('q', '')
    if query:
        events = events.filter(
            Q(title__icontains=query) | Q(venue__icontains=query) |
            Q(description__icontains=query)
        )

    # Category filter
    category = request.GET.get('category', '')
    if category:
        events = events.filter(category=category)

    events = events.order_by('date')

    context = {
        'events': events,
        'query': query,
        'selected_category': category,
        'categories': Event.CATEGORY_CHOICES,
    }
    return render(request, 'ems/events/list.html', context)


def event_detail(request, slug):
    """Event detail page with registration status."""
    event = get_object_or_404(Event, slug=slug)
    user_registration = None
    if request.user.is_authenticated:
        user_registration = Registration.objects.filter(
            user=request.user, event=event
        ).first()

    context = {
        'event': event,
        'user_registration': user_registration,
    }
    return render(request, 'ems/events/detail.html', context)


@login_required
@role_required('manager', 'admin')
def event_create(request):
    """Create a new event."""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('event_detail', slug=event.slug)
        messages.error(request, "Please fix the errors below.")
    else:
        form = EventForm()
    return render(request, 'ems/events/form.html', {'form': form, 'action': 'Create'})


@login_required
@role_required('manager', 'admin')
def event_edit(request, slug):
    """Edit an existing event (owner or admin only)."""
    event = get_object_or_404(Event, slug=slug)

    # Non-admin managers can only edit their own events
    if request.user.profile.role == 'manager' and event.created_by != request.user:
        messages.error(request, "You can only edit your own events.")
        return redirect('event_list')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
        # Pre-fill datetime-local field
        if event.date:
            form.fields['date'].initial = event.date.strftime('%Y-%m-%dT%H:%M')

    return render(request, 'ems/events/form.html', {'form': form, 'event': event, 'action': 'Edit'})


@login_required
@role_required('manager', 'admin')
def event_delete(request, slug):
    """Delete an event (with confirmation)."""
    event = get_object_or_404(Event, slug=slug)
    if request.user.profile.role == 'manager' and event.created_by != request.user:
        messages.error(request, "You can only delete your own events.")
        return redirect('event_list')

    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f"Event '{title}' has been deleted.")
        return redirect('manager_events')

    return render(request, 'ems/events/delete_confirm.html', {'event': event})


@login_required
@role_required('manager', 'admin')
def manager_events(request):
    """Event manager's own event list."""
    if request.user.profile.role == 'admin':
        events = Event.objects.all().select_related('created_by')
    else:
        events = Event.objects.filter(created_by=request.user)
    return render(request, 'ems/events/manager_list.html', {'events': events})


# ══════════════════════════════════════════════
# REGISTRATION VIEWS
# ══════════════════════════════════════════════

@login_required
@require_POST
def register_for_event(request, slug):
    """Register the current user for an event."""
    event = get_object_or_404(Event, slug=slug, status='published')

    # Block managers from registering
    if request.user.profile.role == 'manager':
        messages.warning(request, "Event Managers cannot register for events.")
        return redirect('event_detail', slug=slug)

    # Check for duplicate
    if Registration.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, "You're already registered for this event.")
        return redirect('event_detail', slug=slug)

    # Determine status: confirmed or waitlisted
    status = 'waitlisted' if event.is_full else 'confirmed'
    Registration.objects.create(user=request.user, event=event, status=status)

    if status == 'confirmed':
        messages.success(request, f"🎉 Successfully registered for '{event.title}'!")
    else:
        messages.info(request, f"Event is full. You've been added to the waitlist for '{event.title}'.")

    return redirect('event_detail', slug=slug)



@login_required
def my_registrations(request):
    """Attendee's personal registration history."""
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registered_at')
    return render(request, 'ems/registrations/my_list.html', {'registrations': registrations})


@login_required
@role_required('manager', 'admin')
def event_registrations(request, slug):
    """View all registrations for a specific event."""
    event = get_object_or_404(Event, slug=slug)
    if request.user.profile.role == 'manager' and event.created_by != request.user:
        messages.error(request, "Access denied.")
        return redirect('manager_events')

    registrations = event.registrations.select_related('user').order_by('-registered_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        registrations = registrations.filter(status=status_filter)

    return render(request, 'ems/registrations/event_list.html', {
        'event': event,
        'registrations': registrations,
        'status_filter': status_filter,
    })


# ══════════════════════════════════════════════
# REGISTRATION CANCEL VIEWS
# ══════════════════════════════════════════════


def send_cancellation_email(registration):
    send_mail(
        subject=f"❌ Registration Cancelled — {registration.event.title}",
        message=f"Your registration has been cancelled.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.user.email],
        fail_silently=False,
    )



@login_required
@require_POST
def cancel_registration(request, reg_id):
    registration = get_object_or_404(Registration, registration_id=reg_id)

    if registration.user != request.user and request.user.profile.role not in ('admin', 'manager'):
        messages.error(request, "You cannot cancel someone else's registration.")
        return redirect('my_registrations')

    if registration.status == 'cancelled':
        messages.warning(request, "This registration is already cancelled.")
        return redirect('my_registrations')

    promoted = registration.cancel()

    # ✅ SENDING EMAIL EXPLICITLY
    send_cancellation_email(registration)

    messages.success(request, f"Registration cancelled for '{registration.event.title}'.")

    if promoted:
        messages.info(request, "A waitlisted attendee has been promoted to confirmed.")
        _send_confirmation_email(promoted)
    return redirect('my_registrations')






# ══════════════════════════════════════════════
# ANALYTICS VIEWS
# ══════════════════════════════════════════════

@login_required
@role_required('admin', 'manager')
def analytics_dashboard(request):
    """Analytics dashboard page (charts rendered via JS API calls)."""
    return render(request, 'ems/analytics/dashboard.html')


@login_required
@role_required('admin', 'manager')
def api_category_distribution(request):
    """JSON: event count per category (Pie chart)."""
    if request.user.profile.role == 'manager':
        qs = Event.objects.filter(created_by=request.user)
    else:
        qs = Event.objects.all()

    data = list(
        qs.values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    # Humanize category labels
    category_map = dict(Event.CATEGORY_CHOICES)
    result = [[category_map.get(d['category'], d['category']), d['count']] for d in data]
    return JsonResponse({'data': result})


@login_required
@role_required('admin', 'manager')
def api_monthly_registrations(request):
    """JSON: monthly registration counts for the past 12 months (Line chart)."""
    twelve_months_ago = timezone.now() - timedelta(days=365)

    if request.user.profile.role == 'manager':
        qs = Registration.objects.filter(event__created_by=request.user)
    else:
        qs = Registration.objects.all()

    qs = qs.filter(registered_at__gte=twelve_months_ago)

    # Build month-by-month counts
    monthly = {}
    for reg in qs:
        key = reg.registered_at.strftime('%b %Y')
        monthly[key] = monthly.get(key, 0) + 1

    # Fill in missing months with 0
    result = []
    for i in range(11, -1, -1):
        d = timezone.now() - timedelta(days=30 * i)
        key = d.strftime('%b %Y')
        result.append([key, monthly.get(key, 0)])

    return JsonResponse({'data': result})


@login_required
@role_required('admin', 'manager')
def api_event_registrations(request):
    """JSON: top events by registration count (Bar chart)."""
    if request.user.profile.role == 'manager':
        qs = Event.objects.filter(created_by=request.user)
    else:
        qs = Event.objects.all()

    data = list(
        qs.annotate(reg_count=Count('registrations'))
        .values('title', 'reg_count')
        .order_by('-reg_count')[:10]
    )
    result = [[d['title'][:30], d['reg_count']] for d in data]
    return JsonResponse({'data': result})


@login_required
@role_required('admin', 'manager')
def api_seat_occupancy(request):
    """JSON: overall seat occupancy percentage (Gauge chart)."""
    if request.user.profile.role == 'manager':
        events = Event.objects.filter(created_by=request.user, status='published')
    else:
        events = Event.objects.filter(status='published')

    total_seats = sum(e.total_seats for e in events)
    confirmed = Registration.objects.filter(
        event__in=events, status='confirmed'
    ).count()

    occupancy = round((confirmed / total_seats * 100), 1) if total_seats > 0 else 0
    return JsonResponse({'occupancy': occupancy, 'confirmed': confirmed, 'total': total_seats})


# ══════════════════════════════════════════════
# PROFILE VIEWS
# ══════════════════════════════════════════════

@login_required
def profile_view(request):
    """View own profile."""
    return render(request, 'ems/profile/view.html', {
        'profile': request.user.profile
    })


@login_required
def profile_edit(request):
    """Edit own profile."""
    if request.method == 'POST':
        form = ProfileForm(
            request.POST, request.FILES,
            instance=request.user.profile,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_view')
        messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileForm(instance=request.user.profile, user=request.user)
    return render(request, 'ems/profile/edit.html', {'form': form})


# ══════════════════════════════════════════════
# ADMIN VIEWS
# ══════════════════════════════════════════════

@login_required
@role_required('admin')
def admin_users(request):
    """Admin: manage all users and their roles."""
    users = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'ems/admin/users.html', {'users': users})


@login_required
@role_required('admin')
def admin_user_role(request, user_id):
    """Admin: change a user's role."""
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Role updated for {user.username}.")
            return redirect('admin_users')
    else:
        form = UserRoleForm(instance=user.profile)
    return render(request, 'ems/admin/user_role.html', {'form': form, 'target_user': user})


@login_required
@role_required('admin')
def export_registrations_csv(request):
    """Admin: export all registrations as CSV download."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="ems_registrations_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'Registration ID', 'Event', 'Category', 'Event Date',
        'Attendee Username', 'Attendee Name', 'Attendee Email',
        'Status', 'Registered At'
    ])

    registrations = Registration.objects.select_related(
        'user', 'event'
    ).order_by('-registered_at')

    for reg in registrations:
        writer.writerow([
            reg.registration_id,
            reg.event.title,
            reg.event.get_category_display(),
            reg.event.date.strftime('%Y-%m-%d %H:%M'),
            reg.user.username,
            reg.user.get_full_name(),
            reg.user.email,
            reg.get_status_display(),
            reg.registered_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


@login_required
@role_required('admin')
def export_events_csv(request):
    """Admin: export all events as CSV download."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="ems_events_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Category', 'Venue', 'Date', 'Total Seats',
        'Confirmed', 'Available', 'Status', 'Created By', 'Created At'
    ])

    for event in Event.objects.select_related('created_by').order_by('-created_at'):
        writer.writerow([
            event.title,
            event.get_category_display(),
            event.venue,
            event.date.strftime('%Y-%m-%d %H:%M'),
            event.total_seats,
            event.confirmed_registrations,
            event.available_seats,
            event.get_status_display(),
            event.created_by.username,
            event.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response
