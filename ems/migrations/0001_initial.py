# Generated migration for EMS models
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Event Manager'), ('attendee', 'Attendee')], default='attendee', max_length=20)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('phone', models.CharField(blank=True, max_length=15)),
                ('bio', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('conference', 'Conference'), ('workshop', 'Workshop'), ('seminar', 'Seminar'), ('webinar', 'Webinar'), ('concert', 'Concert'), ('sports', 'Sports'), ('networking', 'Networking'), ('hackathon', 'Hackathon'), ('exhibition', 'Exhibition'), ('other', 'Other')], max_length=50)),
                ('venue', models.CharField(max_length=300)),
                ('date', models.DateTimeField()),
                ('total_seats', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='draft', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='event_banners/')),
                ('tags', models.CharField(blank=True, help_text='Comma-separated tags', max_length=200)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-date']},
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['status', 'date'], name='ems_event_status_date_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['category'], name='ems_event_category_idx'),
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.CharField(editable=False, max_length=12, unique=True)),
                ('status', models.CharField(choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('waitlisted', 'Waitlisted')], default='confirmed', max_length=20)),
                ('registered_at', models.DateTimeField(auto_now_add=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='ems.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-registered_at']},
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together={('user', 'event')},
        ),
        migrations.AddIndex(
            model_name='registration',
            index=models.Index(fields=['status'], name='ems_registration_status_idx'),
        ),
        migrations.AddIndex(
            model_name='registration',
            index=models.Index(fields=['registered_at'], name='ems_registration_date_idx'),
        ),
    ]
