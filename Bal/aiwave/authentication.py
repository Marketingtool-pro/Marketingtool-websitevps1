from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from wowdash_app.utils import log_error_to_file
from Dal.aiwave.authentication import (
    get_user_by_email_dal,
    get_user_by_username_dal,
    check_user_exists_by_username_dal,
    check_user_exists_by_email_dal,
    authenticate_user_dal,
    create_user_with_profile_dal,
    delete_user_dal,
    delete_user_session_by_key_dal,
    check_user_profile_active_dal,
    get_user_profile_role_dal,
    send_welcome_email_dal,
    set_user_otp_dal,
    update_user_password_dal,
    get_user_otp_dal,
    send_otp_email_dal
)
from wowdash_app.models import User
from django.utils import timezone

def validate_signin_data_bal(email, password):
    """Validate signin data"""
    try:
        if not email or not password:
            raise ValueError("Please provide both email and password.")
        return True
    except Exception as e:
        log_error_to_file(e)

def process_user_signin_bal(email, password):
    """Process user signin"""
    try:
        # Find user by email first
        user = get_user_by_email_dal(email)
        
        # Check if user's profile is active
        if not check_user_profile_active_dal(user):
            raise ValueError("Your account has been deactivated. Please contact the administrator.")
        
        # Then authenticate with username
        authenticated_user = authenticate_user_dal(user.username, password)
        if authenticated_user is None:
            raise ValueError("Invalid password.")
        
        return authenticated_user
    except User.DoesNotExist:
        raise ValueError("No account found with this email.")
    except Exception as e:
        log_error_to_file(e)

def process_user_signin_by_username_bal(username, password):
    """Process user signin by username (for future features)"""
    try:
        # Find user by username
        user = get_user_by_username_dal(username)
        
        # Check if user's profile is active
        if not check_user_profile_active_dal(user):
            raise ValueError("Your account has been deactivated. Please contact the administrator.")
        
        # Authenticate with username
        authenticated_user = authenticate_user_dal(username, password)
        if authenticated_user is None:
            raise ValueError("Invalid password.")
        
        return authenticated_user
    except User.DoesNotExist:
        raise ValueError("No account found with this username.")
    except Exception as e:
        log_error_to_file(e)

def validate_signup_data_bal(username, email, password):
    """Validate signup data"""
    try:
        if not username or not email or not password:
            raise ValueError("Please fill every details.")
        return True
    except Exception as e:
        log_error_to_file(e)

def check_signup_duplicates_bal(username, email):
    """Check for duplicate username or email during signup"""
    try:
        # Check if username already exists
        if check_user_exists_by_username_dal(username):
            raise ValueError("Username already exists.")
        
        # Check if email already exists
        if check_user_exists_by_email_dal(email):
            raise ValueError("Email already registered.")
        
        return True
    except Exception as e:
        log_error_to_file(e)

def process_user_signup_bal(username, email, password):
    """Process user signup"""
    try:
        # Create user with profile
        user = create_user_with_profile_dal(username, email, password)
        
        # Authenticate the newly created user
        authenticated_user = authenticate_user_dal(username, password)
        if authenticated_user is None:
            raise ValueError("Authentication failed after signup.")
        
        # Send welcome email
        send_welcome_email_dal(email, username)
        
        return authenticated_user
    except Exception as e:
        log_error_to_file(e)

def validate_password_for_deletion_bal(user, password):
    """Validate password for account deletion"""
    try:
        if not password:
            raise ValueError("Password is required to delete your account")
        
        # Verify password
        if not check_password(password, user.password):
            raise ValueError("Incorrect password. Please try again.")
        
        return True
    except Exception as e:
        log_error_to_file(e)

def process_account_deletion_bal(user):
    """Process account deletion"""
    try:
        # Delete the user (this will cascade delete the profile)
        delete_user_dal(user)
        return True
    except Exception as e:
        log_error_to_file(e)

def cleanup_user_session_bal(session_key):
    """Clean up user session"""
    try:
        delete_user_session_by_key_dal(session_key)
        return True
    except Exception as e:
        log_error_to_file(e)

def get_user_redirect_url_bal(user):
    """Get redirect URL based on user role"""
    try:
        role = get_user_profile_role_dal(user)
        if role == 'admin':
            return 'wowdash-index'
        else:
            return 'aiwave-index'
    except Exception as e:
        log_error_to_file(e)

def process_password_reset_bal(request):
    """Business logic for password reset process"""
    try:
        email = request.POST.get('email')
        if not email:
            return False, 'Please provide an email address.'
        # Check if the email exists in the database
        user = get_user_by_email_dal(email)
        if not user:
            return False, 'No account found with this email address.'
        # Generate and set OTP
        otp = set_user_otp_dal(user)
        return True, otp
    except Exception as e:
        log_error_to_file(e)

def validate_otp_bal(userotp, otp_input):
    """Business logic for OTP validation"""
    try:
        if not otp_input or len(str(otp_input)) < 4:
            return False, "Please enter the OTP."
        if not userotp:
            return False, "OTP record not found."
        if userotp.otp_valid_until and timezone.now() > userotp.otp_valid_until:
            return False, "OTP expired. Please request a new OTP."
        if str(userotp.reset_otp) == str(otp_input):
            # Clear the OTP data on successful verification
            userotp.reset_otp = None
            userotp.otp_valid_until = None
            userotp.save()
            return True, "OTP verified successfully"
        return False, "Invalid OTP. Please try again."
    except Exception as e:
        log_error_to_file(e)

def validate_passwords_bal(request):
    """Business logic for password validation and update"""
    try:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if not new_password or not confirm_password:
            return False, "Both password fields are required."
        elif new_password != confirm_password:
            return False, "Passwords do not match."
        elif len(new_password) < 6:
            return False, "Password must be at least 6 characters long."
        # Get user from session email
        from wowdash_app import utils
        reset_email = utils.get_reset_email(request)
        if not reset_email:
            return False, "Session expired. Please try again."
        user = get_user_by_email_dal(reset_email)
        if not user:
            return False, "User not found."
        # Ensure new password is unique (not same as previous)
        if check_password(new_password, user.password):
            return False, "New password must be different from your previous password."
        # Update password
        update_user_password_dal(user, new_password)
        # Clear session
        del request.session['reset_email']
        return True, "Password successfully reset. Please sign in."
    except Exception as e:
        log_error_to_file(e)

def get_user_and_otp_bal(reset_email):
    """Business logic for getting user and OTP"""
    try:
        user = get_user_by_email_dal(reset_email)
        if not user:
            return None, None
        userotp = get_user_otp_dal(user)
        return user, userotp
    except Exception as e:
        log_error_to_file(e)

def send_otp_email_bal(user, otp, email_template=None, subject='Password Reset OTP', from_email=None):
    """Business logic for sending OTP email"""
    if email_template is None:
        email_template = 'emails/otp_email.html'
    return send_otp_email_dal(user, otp, email_template, subject, from_email)

def get_otp_from_request_bal(request):
    """Business logic for extracting OTP from request"""
    try:
        # If OTP is sent as a single field
        otp = request.POST.get('otp')
        if otp:
            return otp
        # If OTP is sent as multiple fields (e.g., otp[0], otp[1], ...)
        otp_digits = request.POST.getlist('otp')
        if otp_digits:
            return "".join(otp_digits)
        return None
    except Exception as e:
        log_error_to_file(e)

