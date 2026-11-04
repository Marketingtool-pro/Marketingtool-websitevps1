from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from wowdash_app.models import UserSession, UserOTP
from django.db import transaction
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from wowdash_app.utils import log_error_to_file
import random
from wowdash_app.env_cache import get

def get_user_by_email_dal(email):
    """Get user by email"""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        raise User.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def get_user_by_username_dal(username):
    """Get user by username"""
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        raise User.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def check_user_exists_by_username_dal(username):
    """Check if user exists by username"""
    try:
        return User.objects.filter(username=username).exists()
    except Exception as e:
        log_error_to_file(e)

def check_user_exists_by_email_dal(email):
    """Check if user exists by email"""
    try:
        return User.objects.filter(email=email).exists()
    except Exception as e:
        log_error_to_file(e)

def authenticate_user_dal(username, password):
    """Authenticate user with username and password"""
    try:
        return authenticate(username=username, password=password)
    except Exception as e:
        log_error_to_file(e)

def create_user_with_profile_dal(username, email, password):
    """Create user with profile in a transaction"""
    try:
        with transaction.atomic():
            name_parts = username.split() if username else []
            first_name = name_parts[0] if name_parts else ''
            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name
            )
            return user
    except Exception as e:
        log_error_to_file(e)

def delete_user_dal(user):
    """Delete user (this will cascade delete the profile)"""
    try:
        user.delete()
        return True
    except Exception as e:
        log_error_to_file(e)

def delete_user_session_by_key_dal(session_key):
    """Delete user session by session key"""
    try:
        UserSession.objects.filter(session_key=session_key).delete()
        return True
    except Exception as e:
        log_error_to_file(e)

def check_user_profile_active_dal(user):
    """Check if user profile is active"""
    try:
        return user.profile.is_active
    except Exception as e:
        log_error_to_file(e)

def get_user_profile_role_dal(user):
    """Get user profile role"""
    try:
        if user.is_superuser:
            return 'admin'
        if user.is_staff:
            return 'admin'
        return user.profile.role
    except Exception as e:
        log_error_to_file(e)

def get_email_connection_from_envcache():
    email_backend = get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
    email_host = get('EMAIL_HOST', 'smtp.gmail.com')
    email_port = int(get('EMAIL_PORT', 587))
    email_host_user = get('EMAIL_HOST_USER', '')
    email_host_password = get('EMAIL_HOST_PASSWORD', '')
    email_use_tls = get('EMAIL_USE_TLS', 'True') == 'True'
    default_email = get('DEFAULT_FROM_EMAIL')
    connection = get_connection(
        backend=email_backend,
        host=email_host,
        port=email_port,
        username=email_host_user,
        password=email_host_password,
        use_tls=email_use_tls,
        default_email=default_email,
    )
    return connection

def send_welcome_email_dal(to_email, username):
    from_email = get('DEFAULT_FROM_EMAIL', get('EMAIL_HOST_USER', None))
    subject = 'Welcome to AIWave!'
    html_message = render_to_string('emails/welcome_email.html', {'username': username})
    message = f"Hello {username},\n\nThank you for signing up at AIWave. We are excited to have you on board!\n\nBest regards,\nThe AIWave Team"
    connection = get_email_connection_from_envcache()
    send_mail(
        subject,
        message,
        from_email,
        [to_email],
        html_message=html_message,
        fail_silently=True,
        connection=connection,
    )

def set_user_otp_dal(user):
    """Set OTP for user password reset"""
    try:
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        # Set OTP valid for 5 minutes
        otp_valid_until = timezone.now() + timedelta(minutes=5)
        # Update or create OTP record
        user_otp, created = UserOTP.objects.get_or_create(user=user)
        user_otp.reset_otp = otp
        user_otp.otp_valid_until = otp_valid_until
        user_otp.save()
        return otp
    except Exception as e:
        log_error_to_file(e)

def update_user_password_dal(user, new_password):
    """Update user password"""
    try:
        user.password = make_password(new_password)
        user.save()
        return user
    except Exception as e:
        log_error_to_file(e)

def get_user_otp_dal(user):
    """Get user OTP record"""
    from wowdash_app.models import UserOTP
    try:
        return UserOTP.objects.get(user=user)
    except UserOTP.DoesNotExist:
        return None
    except Exception as e:
        log_error_to_file(e)

def send_otp_email_dal(user, otp, email_template, subject, from_email=None):
    from django.template.loader import render_to_string
    context = {'user': user, 'otp': otp, 'valid_minutes': 5}
    email_html = render_to_string(email_template, context)
    if not from_email:
        from_email = get('DEFAULT_FROM_EMAIL', get('EMAIL_HOST_USER', None))
    message = f'Your OTP for password reset is: {otp}. Valid for 5 minutes.'
    connection = get_email_connection_from_envcache()
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[user.email],
        html_message=email_html,
        fail_silently=False,
        connection=connection,
    )

