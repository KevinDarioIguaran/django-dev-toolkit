from django.apps import AppConfig


class DjangoDevToolkitConfig(AppConfig):
    name = 'django_dev_toolkit'
    
    def ready(self):
        import django_dev_toolkit.signals
