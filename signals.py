from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Language
from .languages import generate_languages_file

import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Language)
def language_pre_save(sender, instance, **kwargs):
    """Saves the previous state before saving"""
    if instance.pk:
        try:
            instance._original_state = Language.objects.get(pk=instance.pk)
        except Language.DoesNotExist:
            instance._original_state = None
    else:
        instance._original_state = None

@receiver(post_save, sender=Language)
def language_post_save(sender, instance, created, **kwargs):
    """Regenerates language file when a language is created or modified"""
    try:
        generate_languages_file()
        action = "created" if created else "modified"
        logger.info(f"Language {action}: {instance.name} ({instance.code})")
    except Exception as e:
        logger.error(f"Error regenerating language file after save: {e}")

@receiver(post_delete, sender=Language)
def language_post_delete(sender, instance, **kwargs):
    """Regenerates language file when a language is deleted"""
    try:
        generate_languages_file()
        logger.info(f"Language removed: {instance.name} ({instance.code})")
    except Exception as e:
        logger.error(f"Error regenerating language file after deletion: {e}")

