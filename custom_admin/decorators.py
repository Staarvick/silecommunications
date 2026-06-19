from django.shortcuts import redirect
from django.contrib import messages


def custom_admin_required(view_func):
    """Simple decorator to check if user is custom admin"""

    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Please login first')
            return redirect('accounts:login')

        # Check if user is a custom admin (you can add specific users here)
        if not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')

        return view_func(request, *args, **kwargs)

    return wrapper