from wowdash_app.models import EnvVar
from wowdash_app.utils import log_error_to_file

def get_all_env_vars():
    """Get all environment variables as a dictionary"""
    try:
        return {v.key: v.value for v in EnvVar.objects.all()}
    except Exception as e:
        log_error_to_file(e)

def update_or_create_env_var(key, value):
    """Update or create an environment variable"""
    try:
        EnvVar.objects.update_or_create(key=key, defaults={'value': value})
        return True
    except Exception as e:
        log_error_to_file(e)

def update_multiple_env_vars(post_data):
    """Update multiple environment variables from POST data"""
    try:
        for key, value in post_data.items():
            if key != 'csrfmiddlewaretoken':
                update_or_create_env_var(key, value)
        return True
    except Exception as e:
        log_error_to_file(e)
