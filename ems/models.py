"""
EMS Models: Profile, Event, Registration
Clean architecture with proper constraints and integrity.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


# ──────────────────────────────────────────────
# PROFILE MODEL
# ──────────────────────────────────────────────
class Profile(models.Model):
    """
    Extends Django User with role and avatar.
    Auto-created via signal when User is saved.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Event Manager'),
        ('attendee', 'Attendee'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_attendee(self):
        return self.role == 'attendee'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/ems/img/default_avatar.svg'


# ──────────────────────────────────────────────
# EVENT MODEL
# ──────────────────────────────────────────────
class Event(models.Model):
    """
    Core event entity managed by Event Managers.
    """
    CATEGORY_CHOICES = [
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
        ('webinar', 'Webinar'),
        ('concert', 'Concert'),
        ('sports', 'Sports'),
        ('networking', 'Networking'),
        ('hackathon', 'Hackathon'),
        ('exhibition', 'Exhibition'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    venue = models.CharField(max_length=300)
    date = models.DateTimeField()
    total_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='managed_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    banner = models.ImageField(upload_to='event_banners/', blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['status', 'date']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import random, string
            base_slug = slugify(self.title)
            unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    @property
    def confirmed_registrations(self):
        return self.registrations.filter(status='confirmed').count()

    @property
    def available_seats(self):
        return self.total_seats - self.confirmed_registrations

    @property
    def is_full(self):
        return self.available_seats <= 0

    @property
    def occupancy_percentage(self):
        if self.total_seats == 0:
            return 0
        return round((self.confirmed_registrations / self.total_seats) * 100, 1)

    @property
    def is_past(self):
        return self.date < timezone.now()

    @property
    def is_published(self):
        return self.status == 'published'


# ──────────────────────────────────────────────
# REGISTRATION MODEL
# ──────────────────────────────────────────────
class Registration(models.Model):
    """
    Tracks user registrations to events.
    Unique constraint prevents duplicate registrations.
    """
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('waitlisted', 'Waitlisted'),
    ]

    registration_id = models.CharField(max_length=12, unique=True, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='registrations'
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='registrations'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        # Prevent duplicate registrations for same user+event
        unique_together = [('user', 'event')]
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['registered_at']),
        ]

    def __str__(self):
        return f"{self.registration_id} — {self.user.username} @ {self.event.title}"

    def save(self, *args, **kwargs):
        # Auto-generate unique 8-char registration ID
        if not self.registration_id:
            self.registration_id = self._generate_reg_id()
        super().save(*args, **kwargs)

    def _generate_reg_id(self):
        """Generate a unique uppercase registration ID like 'EMS-A3F7K2'."""
        while True:
            reg_id = 'EMS-' + uuid.uuid4().hex[:6].upper()
            if not Registration.objects.filter(registration_id=reg_id).exists():
                return reg_id

    def cancel(self):
        """Cancel this registration and promote a waitlisted attendee."""

        if self.status == 'cancelled':
            return None

        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()

        #  Calculate available seats
        confirmed_count = self.event.registrations.filter(status='confirmed').count()

        if confirmed_count >= self.event.total_seats:
            return None  # no available seats

        #  Promote next waitlisted (FIFO)
        next_waitlisted = (
            self.event.registrations
            .filter(status='waitlisted')
            .order_by('registered_at')  # or created_at
            .first()
        )

        if next_waitlisted:
            next_waitlisted.status = 'confirmed'
            next_waitlisted.save()
            return next_waitlisted

        return None