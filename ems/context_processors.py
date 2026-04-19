"""
Global context processor: injects user role into all templates.
"""


def user_role(request):
    """Make user role available in all templates as {{ user_role }}."""
    if request.user.is_authenticated:
        try:
            role = request.user.profile.role
        except Exception:
            role = 'attendee'
    else:
        role = None
    return {'user_role': role}
