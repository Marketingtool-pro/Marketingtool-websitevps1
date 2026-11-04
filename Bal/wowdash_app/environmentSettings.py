from Dal.wowdash_app.environmentSettings import get_all_env_vars, update_multiple_env_vars
from wowdash_app.utils import log_error_to_file

def get_environment_variables():
    """Get all environment variables for display"""
    try:
        return get_all_env_vars()
    except Exception as e:
        log_error_to_file(e)

def update_environment_settings(post_data):
    """Update environment settings from POST data"""
    try:
        update_multiple_env_vars(post_data)
        return True
    except Exception as e:
        log_error_to_file(e)
