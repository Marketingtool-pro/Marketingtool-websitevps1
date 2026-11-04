from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from wowdash_app.models import UserOTP
from wowdash_app.utils import generate_otp
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.files.storage import default_storage
import os
from django.conf import settings

def create_user_profile_dal(username, email, password):
    """
    Create a new user with the given username, email, and password.
    The password is hashed before saving.
    """
    user = User(
        username=username,
        email=email,
        password=make_password(password)  # Hash the password before saving
    )
    user.save()
    return user

def set_user_otp_profile_dal(user):
    """
    Generate and store an OTP for the given user in the UserOTP model.
    Returns the generated OTP.
    """
    otp = generate_otp()
    userotp, created = UserOTP.objects.get_or_create(user=user)
    userotp.reset_otp = otp
    userotp.otp_valid_until = timezone.now() + timezone.timedelta(minutes=5)
    userotp.save()
    return otp

def get_user_by_id(user_id):
    return User.objects.get(id=user_id)

def get_user_by_email_profile_dal(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

def get_all_users_with_profiles():
    return User.objects.select_related('profile').order_by('id').all()

def filter_users(search=None, status=None):
    users = User.objects.select_related('profile').filter(profile__isnull=False).order_by('id')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    if status and status != 'Status':
        users = users.filter(profile__is_active=(status == 'Active'))
    return users

def paginate_users(users, page, per_page):
    paginator = Paginator(users, per_page)
    return paginator.get_page(page)

def delete_user(user):
    user.delete()

def get_or_create_content_setting_by_key(key, value=None):
    from wowdash_app.models import ContentSetting
    obj, created = ContentSetting.objects.get_or_create(key=key, defaults={"value": value or ""})
    return obj, created

def update_content_setting_value(obj, value):
    obj.value = value
    obj.save()
    return obj

def get_user_by_email_dal(email):
    from django.contrib.auth.models import User
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None

def get_userotp_by_user_dal(user):
    from wowdash_app.models import UserOTP
    try:
        return UserOTP.objects.get(user=user)
    except UserOTP.DoesNotExist:
        return None

def save_userotp_dal(userotp):
    userotp.save()
    return userotp

def user_exists_by_email_dal(email):
    from django.contrib.auth.models import User
    return User.objects.filter(email=email).exists()

def get_user_profile_dal(user):
    return user.profile

def save_user_profile_dal(profile):
    profile.save()
    return profile

def set_user_password_dal(user, new_password):
    user.set_password(new_password)
    return user

def save_user_dal(user):
    user.save()
    return user

def is_user_superuser_dal(user):
    return user.is_superuser

def save_chat_bot_image_file(file):
    """Save uploaded chat bot image file and return its URL path."""
    try:
        filename = default_storage.save(os.path.join('chat_bot_images', file.name), file)
        return os.path.join(settings.MEDIA_URL, filename)
    except Exception as e:
        from wowdash_app.utils import log_error_to_file
        log_error_to_file(e)
        return ''
