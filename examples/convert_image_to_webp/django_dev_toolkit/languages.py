import logging
from django.conf import settings
import os
import json
import logging

logger = logging.getLogger(__name__)


def generate_languages_file():
    """Generate a JSON file with all available languages in the path /resources/languages"""
    try:
        from .models import Language
        languages = Language.objects.all().order_by('name')
        
        languages_data = []
        for lang in languages:
            languages_data.append({
                'code': lang.code,
                'name': lang.name,
                'is_rtl': lang.is_rtl,
                'country_code': lang.country_code or ''
            })
                    
        languages_dir = os.path.join(settings.BASE_DIR, 'resources', 'languages')
        os.makedirs(languages_dir, exist_ok=True)
        
        languages_file = os.path.join(languages_dir, 'languages.json')
        with open(languages_file, 'w', encoding='utf-8') as f:
            json.dump(languages_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Languages file generated successfully: {len(languages_data)} languages")
        
    except Exception as e:
        logger.error(f"Error generating languages file: {e}")
        raise

def get_languages_settings():
    try:
        languages_file = os.path.join(
            settings.BASE_DIR,
            'resources',
            'languages',
            'languages.json'
        )

        with open(languages_file, 'r', encoding='utf-8') as f:
            languages_data = json.load(f)

        return [
            (lang['code'], lang['name'])
            for lang in languages_data
        ]

    except Exception:
        return [('en', 'English')]

def get_language_info(lang_code):
    """Get language info (name and flag code) from the Language model"""
    try:
        from .models import Language
        language = Language.objects.get(code=lang_code)
        return {
            'name': str(language.name).capitalize(),
            'flag_code': language.country_code if language.country_code else 'un'
        }
    except Language.DoesNotExist:
        return {
            'name': lang_code,
            'flag_code': 'un'
        }
    except Exception:
        return {
            'name': lang_code,
            'flag_code': 'un'
        } 