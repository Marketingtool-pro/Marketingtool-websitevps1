import random
from wowdash_app.env_cache import get
from google import genai as google_genai
import traceback, os, datetime
from django.conf import settings  # Import the settings module
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

# Check for Gemini API key at startup
GEMINI_API_KEY = get("GEMINI_API_KEY")
GEMINI_KEY_MISSING = not GEMINI_API_KEY
if not GEMINI_KEY_MISSING:
    # New google-genai SDK (replaces deprecated google.generativeai)
    client = google_genai.Client(api_key=GEMINI_API_KEY)
    model_name = "gemini-2.5-flash"
    chat_session = client.chats.create(model=model_name)
    # Backwards-compat alias: anything still importing `model` from this module
    # keeps working by pointing to the client instance.
    model = client
else:
    client = None
    model = None
    chat_session = None

FALLBACK_AI_ERROR_MSG = "Sorry, there was an error generating a response."

def send_message_to_gemini(message):
    if GEMINI_KEY_MISSING or not chat_session:
        return FALLBACK_AI_ERROR_MSG
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        return FALLBACK_AI_ERROR_MSG


def generate_otp():
    """Generate a 4-digit OTP as a string."""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def set_reset_email(email, request):
    """
    Set the reset email in the session.
    This is used to verify the user during the password reset process.
    """
    request.session['reset_email'] = email

def get_reset_email(request):
    """
    Get the reset email from the session.
    This is used to verify the user during the password reset process.
    """
    email = request.session.get('reset_email', None)
    return email

def log_error_to_file(exception):
    """Logs the exception details to a file."""
    try:
        current_time = datetime.datetime.now()
        exception_details = traceback.format_exc()

        # Define the path to the 'logs' directory in the base directory
        log_dir = os.path.join(settings.BASE_DIR, 'logs')

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file_path = os.path.join(log_dir, 'accounts_log.txt')

         # Get the last frame where the exception was raised
        tb = traceback.extract_tb(exception.__traceback__)
        if tb:
            last_frame = tb[-1]
            file_name = last_frame.filename
            line_number = last_frame.lineno
            function_name = last_frame.name
        else:
            file_name = "Unknown"
            line_number = "Unknown"
            function_name = "Unknown"

        # Write the error details to the log file
        with open(log_file_path, "a") as file:
            file.write(f"Time: {current_time}\n")
            file.write(f"Location: {file_name}, line {line_number}, in {function_name}\n")
            file.write("Exception occurred:\n")
            file.write(exception_details)
            file.write("\n" + "-"*50 + "\n")  # For readability
        print("[DEBUG] Error logged successfully.")
            
    except Exception as log_error:
        print(f"Failed to log error: {log_error}")
        print("Original exception that couldn't be logged:")
        print(traceback.format_exc())

def log_and_redirect_to_error_page(exception):
    """
    Logs the exception and returns a redirect response to the global error page.
    """
    log_error_to_file(exception)
    return redirect('/aiwave/404/')

def role_required(role):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'profile') or request.user.profile.role != role:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator