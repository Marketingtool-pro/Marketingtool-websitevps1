from Dal.wowdash_app.siteMetaSettings import get_all_site_settings, update_multiple_site_settings, save_site_img_file, save_favicon_logo_file, save_small_logo_file, get_site_image_url, get_favicon_logo_url, get_small_logo_url, get_all_site_images, update_or_create_site_setting
from wowdash_app.utils import log_error_to_file

def get_site_settings(keys=None):
    """Get all or selected site meta settings for display"""
    try:
        all_settings = get_all_site_settings()
        if keys is not None:
            return {k: all_settings.get(k, '') for k in keys}
        return all_settings
    except Exception as e:
        log_error_to_file(e)
        return {}

def update_site_settings(post_data, files=None):
    """Update site meta settings from POST data"""
    try:
        # Handle file uploads first - each to its own specific key
        if files:
            if 'site_img' in files:
                file_url = save_site_img_file(files['site_img'])
                if file_url:
                    # Save site image to 'site_logo' key
                    update_or_create_site_setting('site_logo', file_url)
            
            if 'favicon_logo' in files:
                file_url = save_favicon_logo_file(files['favicon_logo'])
                if file_url:
                    # Save favicon to 'favicon_png' key
                    update_or_create_site_setting('favicon_png', file_url)
            
            if 'small_logo' in files:
                file_url = save_small_logo_file(files['small_logo'])
                if file_url:
                    # Save small logo to 'small_logo' key
                    update_or_create_site_setting('small_logo', file_url)
        
        # Handle other form data (non-file fields)
        data = post_data.copy()
        # Remove file fields from data since we handled them separately
        data.pop('site_img', None)
        data.pop('favicon_logo', None)
        data.pop('small_logo', None)
        
        # Update only the non-file fields
        if data:
            update_multiple_site_settings(data)
        
        return True
    except Exception as e:
        log_error_to_file(e)
        return False

def get_site_image():
    """Get the current site image URL"""
    try:
        return get_site_image_url()
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_favicon_logo():
    """Get the current favicon logo URL"""
    try:
        return get_favicon_logo_url()
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_small_logo():
    """Get the current small logo URL"""
    try:
        return get_small_logo_url()
    except Exception as e:
        log_error_to_file(e)
        return ''

def get_site_images():
    """Get all site image URLs as a dictionary"""
    try:
        return get_all_site_images()
    except Exception as e:
        log_error_to_file(e)
        return {'site_img': '', 'favicon_logo': '', 'small_logo': ''}
