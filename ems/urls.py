"""
EMS URL Patterns — complete routing for all features.
"""
from django.urls import path
from . import views

urlpatterns = [
    # ── Public / Auth ──────────────────────────
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Dashboard ──────────────────────────────
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Events (Public) ────────────────────────
    path('events/', views.event_list, name='event_list'),
    path('events/<slug:slug>/', views.event_detail, name='event_detail'),

    # ── Events (Manager/Admin) ─────────────────
    path('events/create/', views.event_create, name='event_create'),
    path('events/<slug:slug>/edit/', views.event_edit, name='event_edit'),
    path('events/<slug:slug>/delete/', views.event_delete, name='event_delete'),
    path('my-events/', views.manager_events, name='manager_events'),

    # ── Registrations ──────────────────────────
    path('events/<slug:slug>/register/', views.register_for_event, name='register_for_event'),
    path('registrations/<str:reg_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('events/<slug:slug>/attendees/', views.event_registrations, name='event_registrations'),

    # ── Analytics ──────────────────────────────
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('api/analytics/categories/', views.api_category_distribution, name='api_categories'),
    path('api/analytics/monthly/', views.api_monthly_registrations, name='api_monthly'),
    path('api/analytics/events/', views.api_event_registrations, name='api_events'),
    path('api/analytics/occupancy/', views.api_seat_occupancy, name='api_occupancy'),

    # ── Profile ─────────────────────────────────
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # ── Admin ───────────────────────────────────
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/role/', views.admin_user_role, name='admin_user_role'),
    path('admin-panel/export/registrations/', views.export_registrations_csv, name='export_registrations'),
    path('admin-panel/export/events/', views.export_events_csv, name='export_events'),
]
