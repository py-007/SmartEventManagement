"""
Role-Based Access Control decorators.
Usage:
    @role_required('admin')
    @role_required('manager', 'admin')
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Restrict view access to users with specified role(s).
    Redirects unauthorized users with a flash message.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            try:
                user_role = request.user.profile.role
            except AttributeError:
                messages.error(request, "Profile not found. Contact administrator.")
                return redirect('home')

            if user_role not in roles:
                messages.error(
                    request,
                    f"Access denied. This section requires: {', '.join(r.title() for r in roles)} role."
                )
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def login_required_custom(view_func):
    """Simple login-required decorator that redirects to login."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to continue.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
