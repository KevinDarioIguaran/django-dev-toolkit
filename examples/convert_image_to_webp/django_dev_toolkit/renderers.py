from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings


"""
Renderers module for Django Dev Toolkit.

This module provides the MessageRenderer class, which is responsible for
rendering different types of messages (error, success, warning, info) as
HTML templates. It handles parsing content from various formats (strings,
dicts, lists) and renders them using Django's template system.
"""


class MessageRenderer:
    """
    Renders messages of different types as HTML templates.

    This class handles the rendering of messages with types: error, success,
    warning, and info. It parses content from various formats and renders
    them using Django's template system with configurable template paths.

    Attributes:
        TYPES (list): Valid message types.
        message_type (str): The type of message to render.
        content (str): The parsed content of the message.
    """

    TYPES = ['error', 'success', 'warning', 'info']

    def __init__(self, message_type, content):
        if message_type not in self.TYPES:
            raise ValueError(f"Invalid type: '{message_type}'. Options: {self.TYPES}")
        self.message_type = message_type
        self.content = self._parse(content)

    def _parse(self, content):
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            return ' '.join(
                error
                for errors in content.values()
                for error in (errors if isinstance(errors, list) else [errors])
            )
        if isinstance(content, (list, tuple)):
            return ' '.join(str(item) for item in content)
        return str(content)

    def render(self):
        base = getattr(settings, 'MESSAGE_URL_TEMPLATES', 'django_dev_toolkit/messages-backend')
        return render_to_string(f"{base}/_{self.message_type}.html", {'content': self.content})