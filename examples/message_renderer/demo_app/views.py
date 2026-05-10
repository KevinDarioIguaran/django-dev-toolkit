from django.shortcuts import render
from django_dev_toolkit import renderers


def home(request):
    messages = {
        'error_message': renderers.MessageRenderer(
            'error',
            'There was a problem processing your request. Please try again later.'
        ).render(),
        'success_message': renderers.MessageRenderer(
            'success',
            'Your changes have been saved successfully! Everything is up to date.'
        ).render(),
        'warning_message': renderers.MessageRenderer(
            'warning',
            'Your subscription is about to expire. Renew now to avoid interruption.'
        ).render(),
        'info_message': renderers.MessageRenderer(
            'info',
            'New feature released: you can now preview messages directly from the dashboard.'
        ).render(),
    }
    return render(request, 'home.html', messages)
