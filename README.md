# 🗓️ EMS — Event Management System

A production-ready Django web application for managing the full lifecycle of events — from creation to analytics.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Role-Based Access** | Admin, Event Manager, Attendee |
| **Event Management** | Create, edit, delete, publish/unpublish |
| **Smart Registration** | Seat tracking, waitlist promotion, cancel & auto-promote |
| **Analytics Dashboard** | Google Charts: Pie, Line, Bar, Gauge |
| **Email Notifications** | HTML emails via Django signals (SMTP) |
| **Profile System** | Avatar upload, bio, registration history |
| **CSV Export** | Admin exports for events and registrations |
| **Responsive UI** | Bootstrap 5, custom CSS, mobile-first |

---

## 🚀 Quick Start

### Option A — Automated Setup Script

```bash
git clone <repo-url>
cd ems_project
chmod +x setup.sh
./setup.sh
python manage.py runserver
```

### Option B — Manual Setup

```bash
# 1. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Seed demo data (optional but recommended)
python manage.py seed_data

# 5. Start development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## 🔐 Demo Accounts

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Admin |
| `alice_mgr` | `manager123` | Event Manager |
| `bob_mgr` | `manager123` | Event Manager |
| `john_doe` | `attendee123` | Attendee |
| `jane_smith` | `attendee123` | Attendee |

---

## 📁 Project Structure

```
ems_project/
├── config/                    # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── ems/                       # Main application
│   ├── models.py              # Profile, Event, Registration
│   ├── views.py               # All views (auth, events, registrations, analytics)
│   ├── urls.py                # URL routing
│   ├── forms.py               # All forms
│   ├── signals.py             # Profile auto-create + email notifications
│   ├── decorators.py          # RBAC decorators
│   ├── admin.py               # Django admin
│   ├── context_processors.py  # Global template context
│   ├── apps.py                # App config (signals registration)
│   ├── migrations/
│   ├── templatetags/
│   │   └── ems_tags.py        # Custom template filters
│   ├── templates/ems/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── auth/              # login.html, register.html
│   │   ├── events/            # list, detail, form, manager_list, delete_confirm
│   │   ├── registrations/     # my_list, event_list
│   │   ├── analytics/         # dashboard.html (Google Charts)
│   │   ├── profile/           # view.html, edit.html
│   │   ├── admin/             # users.html, user_role.html
│   │   ├── emails/            # HTML email templates
│   │   └── partials/          # event_card.html
│   ├── static/ems/
│   │   ├── css/main.css
│   │   ├── js/main.js
│   │   └── img/default_avatar.svg
│   └── management/commands/
│       └── seed_data.py
├── manage.py
├── requirements.txt
└── setup.sh
```

---

## 📊 Database Schema

```
User (Django built-in)
  └── Profile (OneToOne)
        role: admin | manager | attendee
        avatar, phone, bio

Event
  created_by → User (Manager)
  title, description, category, venue, date
  total_seats, status, banner, tags

Registration
  user → User
  event → Event
  UNIQUE (user, event)          ← prevents duplicates
  registration_id               ← auto-generated "EMS-XXXXXX"
  status: confirmed | waitlisted | cancelled
```

---

## 🌐 URL Map

| URL | View | Access |
|---|---|---|
| `/` | Home / Landing | Public |
| `/events/` | Browse Events | Public |
| `/events/<slug>/` | Event Detail | Public |
| `/register/` | Sign Up | Public |
| `/login/` | Login | Public |
| `/dashboard/` | Role Dashboard | Logged In |
| `/events/create/` | Create Event | Manager/Admin |
| `/events/<slug>/edit/` | Edit Event | Owner/Admin |
| `/events/<slug>/delete/` | Delete Event | Owner/Admin |
| `/my-events/` | Manager's Events | Manager/Admin |
| `/events/<slug>/register/` | Register (POST) | Attendee |
| `/my-registrations/` | My Tickets | Attendee |
| `/analytics/` | Charts Dashboard | Manager/Admin |
| `/api/analytics/categories/` | JSON: Category Pie | Manager/Admin |
| `/api/analytics/monthly/` | JSON: Monthly Line | Manager/Admin |
| `/api/analytics/events/` | JSON: Event Bar | Manager/Admin |
| `/api/analytics/occupancy/` | JSON: Gauge | Manager/Admin |
| `/profile/` | View Profile | Logged In |
| `/profile/edit/` | Edit Profile | Logged In |
| `/admin-panel/users/` | User Management | Admin |
| `/admin-panel/export/registrations/` | CSV Export | Admin |
| `/admin-panel/export/events/` | CSV Export | Admin |
| `/admin/` | Django Admin | Superuser |

---

## ⚙️ Email Configuration

Edit `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'   # Gmail App Password
DEFAULT_FROM_EMAIL = 'EMS <your-email@gmail.com>'
```

> For development without SMTP, switch to console backend:
> `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

---

## 🎯 RBAC Summary

| Action | Admin | Manager | Attendee |
|---|:---:|:---:|:---:|
| Create Event | ✅ | ✅ | ❌ |
| Edit Own Events | ✅ | ✅ | ❌ |
| Edit Any Event | ✅ | ❌ | ❌ |
| Delete Event | ✅ | Own only | ❌ |
| View All Attendees | ✅ | Own events | ❌ |
| Register for Events | ❌ | ❌ | ✅ |
| Analytics Dashboard | ✅ | Own events | ❌ |
| Manage Users | ✅ | ❌ | ❌ |
| Export CSV | ✅ | ❌ | ❌ |

---

## 🧪 Test Checklist

- [ ] Register new user as Attendee and Manager
- [ ] Login/logout works for all roles
- [ ] Manager can create, edit, publish, delete events
- [ ] Attendee can register; duplicate registration blocked
- [ ] Event full → Attendee added to waitlist
- [ ] Cancel registration → waitlisted user auto-promoted
- [ ] Analytics charts render (Pie, Line, Bar, Gauge)
- [ ] Profile edit with avatar upload
- [ ] Admin can change user roles
- [ ] CSV export downloads correctly
- [ ] Email sent on registration (check console or SMTP)
- [ ] Unauthorized access redirected with error message

---

## 🛡️ Production Checklist

- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY` from environment variable
- [ ] Configure real SMTP credentials
- [ ] Run `python manage.py collectstatic`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Configure HTTPS / SSL
# SmartEventManagement
# SmartEventManagement
