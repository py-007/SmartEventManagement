"""
Management command to seed the database with demo data.
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

from ems.models import Profile, Event, Registration


class Command(BaseCommand):
    help = 'Seed database with demo users, events, and registrations'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('🌱 Seeding EMS demo data...'))

        # ── Create Admin ────────────────────────
        admin_user, created = User.objects.get_or_create(username='admin')
        if created:
            admin_user.set_password('admin123')
            admin_user.email = 'admin@ems.com'
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            admin_user.profile.role = 'admin'
            admin_user.profile.save()
        self.stdout.write(self.style.SUCCESS('  ✓ Admin user (admin / admin123)'))

        # ── Create Event Managers ────────────────
        managers = []
        for i, (uname, fname, lname, email) in enumerate([
            ('alice_mgr', 'Alice', 'Johnson', 'alice@ems.com'),
            ('bob_mgr', 'Bob', 'Williams', 'bob@ems.com'),
        ]):
            u, created = User.objects.get_or_create(username=uname)
            if created:
                u.set_password('manager123')
                u.email = email
                u.first_name = fname
                u.last_name = lname
                u.save()
                u.profile.role = 'manager'
                u.profile.save()
            managers.append(u)
        self.stdout.write(self.style.SUCCESS('  ✓ 2 Event Managers (password: manager123)'))

        # ── Create Attendees ────────────────────
        attendees = []
        attendee_data = [
            ('john_doe', 'John', 'Doe', 'john@example.com'),
            ('jane_smith', 'Jane', 'Smith', 'jane@example.com'),
            ('raj_kumar', 'Raj', 'Kumar', 'raj@example.com'),
            ('priya_sharma', 'Priya', 'Sharma', 'priya@example.com'),
            ('mike_brown', 'Mike', 'Brown', 'mike@example.com'),
            ('sarah_jones', 'Sarah', 'Jones', 'sarah@example.com'),
            ('arjun_patel', 'Arjun', 'Patel', 'arjun@example.com'),
            ('nina_fox', 'Nina', 'Fox', 'nina@example.com'),
        ]
        for uname, fname, lname, email in attendee_data:
            u, created = User.objects.get_or_create(username=uname)
            if created:
                u.set_password('attendee123')
                u.email = email
                u.first_name = fname
                u.last_name = lname
                u.save()
                u.profile.role = 'attendee'
                u.profile.save()
            attendees.append(u)
        self.stdout.write(self.style.SUCCESS('  ✓ 8 Attendees (password: attendee123)'))

        # ── Create Events ───────────────────────
        events_data = [
            {
                'title': 'PyCon India 2025',
                'description': 'Annual Python conference bringing together developers, data scientists, and engineers from across India. Join us for two days of talks, workshops, and networking.',
                'category': 'conference',
                'venue': 'Bangalore International Convention Centre, Bengaluru',
                'days_from_now': 30,
                'total_seats': 500,
                'status': 'published',
                'manager': managers[0],
            },
            {
                'title': 'Django Workshop: Build REST APIs',
                'description': 'A hands-on workshop where you will build a full REST API using Django REST Framework. Bring your laptop!',
                'category': 'workshop',
                'venue': 'IndiQube Coworking Space, Hyderabad',
                'days_from_now': 15,
                'total_seats': 40,
                'status': 'published',
                'manager': managers[0],
            },
            {
                'title': 'AI/ML Startup Pitch Night',
                'description': 'Top 10 AI/ML startups present their ideas to investors and industry leaders. Great networking opportunity.',
                'category': 'networking',
                'venue': 'The Hive, Mumbai',
                'days_from_now': 7,
                'total_seats': 200,
                'status': 'published',
                'manager': managers[1],
            },
            {
                'title': 'Cloud Architecture Seminar',
                'description': 'Deep dive into modern cloud architecture patterns including microservices, serverless, and Kubernetes.',
                'category': 'seminar',
                'venue': 'Hotel Taj Lands End, Mumbai',
                'days_from_now': 45,
                'total_seats': 150,
                'status': 'published',
                'manager': managers[1],
            },
            {
                'title': 'HackIndia 2025 — National Hackathon',
                'description': '48-hour hackathon with ₹10 lakh prize pool. Teams of 2-4. Theme: Social Impact with AI.',
                'category': 'hackathon',
                'venue': 'IIT Delhi Campus, New Delhi',
                'days_from_now': 60,
                'total_seats': 300,
                'status': 'published',
                'manager': managers[0],
            },
            {
                'title': 'Web3 & Blockchain Webinar',
                'description': 'Online webinar exploring the current state of Web3 development, DeFi, and NFT ecosystems.',
                'category': 'webinar',
                'venue': 'Online (Zoom)',
                'days_from_now': 5,
                'total_seats': 1000,
                'status': 'published',
                'manager': managers[1],
            },
            {
                'title': 'DevOps Best Practices 2025',
                'description': 'Learn CI/CD pipelines, infrastructure as code, and monitoring strategies from industry experts.',
                'category': 'conference',
                'venue': 'Grand Hyatt, Pune',
                'days_from_now': 20,
                'total_seats': 80,
                'status': 'published',
                'manager': managers[0],
            },
            {
                'title': 'Tech Career Fair — Freshers Special',
                'description': 'Connect with 50+ companies hiring fresh graduates in software, data, and design roles.',
                'category': 'exhibition',
                'venue': 'NSIC Grounds, New Delhi',
                'days_from_now': 10,
                'total_seats': 5,  # Small to demo waitlist
                'status': 'published',
                'manager': managers[1],
            },
        ]

        created_events = []
        for ed in events_data:
            if not Event.objects.filter(title=ed['title']).exists():
                event = Event.objects.create(
                    title=ed['title'],
                    description=ed['description'],
                    category=ed['category'],
                    venue=ed['venue'],
                    date=timezone.now() + timedelta(days=ed['days_from_now']),
                    total_seats=ed['total_seats'],
                    status=ed['status'],
                    created_by=ed['manager'],
                )
                created_events.append(event)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(created_events)} Events created'))

        # ── Create Registrations ────────────────
        all_events = Event.objects.filter(status='published')
        reg_count = 0
        for event in all_events:
            # Register random subset of attendees
            sample_size = min(len(attendees), random.randint(2, len(attendees)))
            for attendee in random.sample(attendees, sample_size):
                if not Registration.objects.filter(user=attendee, event=event).exists():
                    status = 'waitlisted' if event.is_full else 'confirmed'
                    Registration.objects.create(
                        user=attendee,
                        event=event,
                        status=status,
                    )
                    reg_count += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {reg_count} Registrations created'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Demo data seeded successfully!'))
        self.stdout.write('')
        self.stdout.write('  Login credentials:')
        self.stdout.write('  👤 admin       / admin123      (Admin)')
        self.stdout.write('  👤 alice_mgr   / manager123    (Event Manager)')
        self.stdout.write('  👤 bob_mgr     / manager123    (Event Manager)')
        self.stdout.write('  👤 john_doe    / attendee123   (Attendee)')
