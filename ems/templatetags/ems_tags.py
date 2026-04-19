"""
Custom template tags and filters for EMS templates.
"""
from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def badge_color(status):
    """Map registration/event status to Bootstrap badge class."""
    mapping = {
        'confirmed': 'success',
        'cancelled': 'danger',
        'waitlisted': 'warning',
        'published': 'success',
        'draft': 'secondary',
        'completed': 'info',
    }
    return mapping.get(status, 'secondary')


@register.filter
def occupancy_color(percentage):
    """Return Bootstrap color class based on occupancy %."""
    if percentage >= 90:
        return 'danger'
    elif percentage >= 70:
        return 'warning'
    return 'success'


@register.filter
def days_until(dt):
    """Return number of days until an event."""
    if not dt:
        return None
    diff = dt - timezone.now()
    return diff.days


@register.simple_tag
def seat_status_badge(event):
    """Return HTML badge for seat availability."""
    if event.is_full:
        return '<span class="badge bg-danger">Sold Out</span>'
    pct = event.occupancy_percentage
    if pct >= 80:
        return f'<span class="badge bg-warning text-dark">Only {event.available_seats} left!</span>'
    return f'<span class="badge bg-success">{event.available_seats} seats available</span>'
