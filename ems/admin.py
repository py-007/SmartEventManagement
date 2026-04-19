"""
EMS Django Admin configuration.
Clean registration with inline support.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Event, Registration


# ── Inline Profile inside User admin ──────────
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ['role', 'phone', 'bio', 'avatar']


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'profile__role']

    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except Profile.DoesNotExist:
            return '—'
    get_role.short_description = 'Role'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'venue', 'date', 'total_seats',
        'confirmed_registrations', 'status', 'created_by'
    ]
    list_filter = ['status', 'category', 'date']
    search_fields = ['title', 'venue', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date']

    def confirmed_registrations(self, obj):
        return obj.confirmed_registrations
    confirmed_registrations.short_description = 'Confirmed'


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'registration_id', 'user', 'event', 'status', 'registered_at'
    ]
    list_filter = ['status', 'registered_at']
    search_fields = ['registration_id', 'user__username', 'event__title']
    readonly_fields = ['registration_id', 'registered_at']
    date_hierarchy = 'registered_at'
    ordering = ['-registered_at']
