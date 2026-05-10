from django.shortcuts import redirect
from django.conf import settings 
from functools import wraps


def no_session_required(view_func):
    """
    Decorator that requires the user to be unauthenticated.
    If the user is authenticated, it redirects them to the homepage.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(getattr(settings, 'INDEX_URL', '/'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


