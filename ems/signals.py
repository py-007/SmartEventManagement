"""
Django signals for EMS:
- Auto-create Profile on User creation
- Send email notifications on registration events
"""
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a new User is created."""
    if created:
        from .models import Profile
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Keep Profile in sync when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender='ems.Registration')
def send_registration_email(sender, instance, created, **kwargs):
    """Send confirmation email when a new registration is created."""
    print("SIGANAL TRIGGERED")
    if not created:
        # Handle status changes (e.g., waitlisted → confirmed)
        if instance.status == 'confirmed':
            _send_confirmation_email(instance)
        return

    try:
        if instance.status == 'confirmed':
            _send_confirmation_email(instance)
        elif instance.status == 'waitlisted':
            _send_waitlist_email(instance)
    except Exception as e:
        logger.error(f"Failed to send registration email: {e}")


def _send_confirmation_email(registration):
    """Send HTML registration confirmation email."""
    print('SIGNAL TRIGGERED')
    context = {
        'registration': registration,
        'user': registration.user,
        'event': registration.event,
    }
    html_message = render_to_string('ems/emails/registration_confirmed.html', context)
    plain_message = (
        f"Hello {registration.user.first_name or registration.user.username},\n\n"
        f"Your registration for '{registration.event.title}' is confirmed!\n"
        f"Registration ID: {registration.registration_id}\n"
        f"Event Date: {registration.event.date.strftime('%B %d, %Y at %I:%M %p')}\n"
        f"Venue: {registration.event.venue}\n\n"
        f"Thank you for registering!"
    )
    try:
        send_mail(
            subject=f"✅ Registration Confirmed — {registration.event.title}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.warning(f"Email not sent (check SMTP config): {e}")


def _send_waitlist_email(registration):
    """Send waitlist notification email."""
    context = {
        'registration': registration,
        'user': registration.user,
        'event': registration.event,
    }
    html_message = render_to_string('ems/emails/registration_waitlisted.html', context)
    plain_message = (
        f"Hello {registration.user.first_name or registration.user.username},\n\n"
        f"You've been added to the waitlist for '{registration.event.title}'.\n"
        f"Waitlist ID: {registration.registration_id}\n"
        f"We'll notify you if a spot opens up.\n\n"
        f"Thank you!"
    )
    try:
        send_mail(
            subject=f"📋 Waitlisted — {registration.event.title}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[registration.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        logger.warning(f"Waitlist email not sent: {e}")
