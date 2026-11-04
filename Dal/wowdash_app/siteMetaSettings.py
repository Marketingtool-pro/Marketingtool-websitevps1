from wowdash_app.models import ContentSetting
from wowdash_app.utils import log_error_to_file
from django.core.files.storage import default_storage
import os
from django.conf import settings

def get_all_site_settings():
    """Get all site meta settings as a dictionary"""
    try:
        return {v.key: v.value for v in ContentSetting.objects.all()}
    except Exception as e:
        log_error_to_file(e)
        return {}

def update_or_create_site_setting(key, value):
    """Update or create a site meta setting"""
    try:
        ContentSetting.objects.update_or_create(key=key, defaults={'value': value})
        return True
    except Exception as e:
        log_error_to_file(e)
        return False

def update_multiple_site_settings(post_data):
    """Update multiple site meta settings from POST data"""
    try:
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                update_or_create_site_setting(key, value)
        return True
    except Exception as e:
        log_error_to_file(e)
        return False

def save_site_img_file(file):
    """Save uploaded site_img file and return its URL path."""
    try:
        filename = default_storage.save(os.path.join('site_settings', 'site_images', file.name), file)
        return os.path.join(settings.MEDIA_URL, filename)
    except Exception as e:
        log_error_to_file(e)
        return ''

def save_favicon_logo_file(file):
    """Save uploaded favicon_logo file and return its URL path."""
    try:
        filename = default_storage.save(os.path.join('site_settings', 'favicon', file.name), file)
        return os.path.join(settings.MEDIA_URL, filename)
    except Exception as e:
        log_error_to_file(e)
        return ''

def save_small_logo_file(file):
    """Save uploaded small_logo file and return its URL path."""
    try:
        filename = default_storage.save(os.path.join('site_settings', 'small_logos', file.name), file)
        return os.path.join(settings.MEDIA_URL, filename)
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_site_image_url():
    """Get the current site image URL"""
    try:
        all_settings = get_all_site_settings()
        return all_settings.get('site_logo', '')
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_favicon_logo_url():
    """Get the current favicon logo URL"""
    try:
        all_settings = get_all_site_settings()
        return all_settings.get('favicon_png', '')
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_small_logo_url():
    """Get the current small logo URL"""
    try:
        all_settings = get_all_site_settings()
        return all_settings.get('small_logo', '')
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_all_site_images():
    """Get all site image URLs as a dictionary"""
    try:
        all_settings = get_all_site_settings()
        return {
            'site_img': all_settings.get('site_logo', ''),
            'favicon_logo': all_settings.get('favicon_png', ''),
            'small_logo': all_settings.get('small_logo', '')
        }
    except Exception as e:
        log_error_to_file(e)
        return {'site_img': '', 'favicon_logo': '', 'small_logo': ''}
