from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from wowdash_app.models import UserOTP
from django.utils import timezone
from Dal.wowdash_app.user import (
    create_user_profile_dal, get_user_by_id, get_all_users_with_profiles, filter_users, paginate_users, delete_user,
    get_or_create_content_setting_by_key, update_content_setting_value,
    get_user_by_email_dal, get_userotp_by_user_dal, save_userotp_dal, user_exists_by_email_dal,
    get_user_profile_dal, save_user_profile_dal, set_user_password_dal, save_user_dal, is_user_superuser_dal,
    save_chat_bot_image_file
)
from django.db import transaction



def check_user_by_email(email):
    """Fetch a user by email."""
    return get_user_by_email_dal(email)


def send_otp_email(user, otp, email_template, subject, from_email):
    """Send OTP email to the user."""
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    context = {'user': user, 'otp': otp, 'valid_minutes': 5}
    email_html = render_to_string(email_template, context)
    send_mail(
        subject=subject,
        message=f'Your OTP for password reset is: {otp}. Valid for 5 minutes.',
        from_email=from_email,
        recipient_list=[user.email],
        html_message=email_html,
        fail_silently=False,
    )
    

def get_otp_from_request(request):
    """
    Retrieves OTP digits from the POST request and concatenates them.
    """
    otp_digits = request.POST.getlist('otp')
    return "".join(otp_digits)


def get_user_and_otp(reset_email: str):
    """
    Retrieves the User object and associated UserOTP object based on the email.
    Returns a tuple (user, userotp) or (None, None) if not found.
    """
    user = get_user_by_email_dal(reset_email)
    if not user:
        return None, None
    userotp = get_userotp_by_user_dal(user)
    if not userotp:
        return None, None
    return user, userotp

    

def validate_otp(userotp, otp_input):
    """
    Validates the OTP and handles success/error messages.
    Returns True if OTP is valid, False otherwise.
    """
    if not otp_input or len(str(otp_input)) < 4:
        return False, "Please enter the OTP."
    
    if not userotp:
        return False, "OTP record not found."

    if userotp.otp_valid_until and timezone.now() > userotp.otp_valid_until:
        return False , "OTP expired. Please request a new OTP."

    if str(userotp.reset_otp) == str(otp_input):
        # Clear the OTP data on successful verification
        userotp.reset_otp = None
        userotp.otp_valid_until = None
        save_userotp_dal(userotp)
        return True, "OTP verified successfully"

    return False, "Invalid OTP. Please try again."

def validate_passwords(request):
    user = None
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')

    if not new_password or not confirm_password:
        return False, "Both password fields are required."
    elif new_password != confirm_password:
        return False, "Passwords do not match."
    elif len(new_password) < 6:
        return False, "Password must be at least 6 characters long."
    elif user:
        # Ensure new password is unique (not same as previous)
        if check_password(new_password, user.password):
            return False, "New password must be different from your previous password."
        else:
            user.password = make_password(new_password)
            user.save()
            del request.session['reset_email']
            return True, "Password successfully reset. Please sign in."

def add_user_bal(name, email, password, department, designation, profile_picture=None):
    if user_exists_by_email_dal(email):
        return None, 'Email already exists'
    with transaction.atomic():
        user = create_user_profile_dal(email, email, password)
        user.is_staff = True     # Optionally, also set as staff
        # Split name into first and last name
        names = name.split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        save_user_dal(user)
        profile = get_user_profile_dal(user)
        profile.department = department
        profile.designation = designation
        if profile_picture:
            profile.profile_picture = profile_picture
        save_user_profile_dal(profile)
    return user, None

def get_users_grid_bal(page, users_per_page=12):
    users_list = get_all_users_with_profiles()
    paginator = paginate_users(users_list, page, users_per_page)
    return paginator

def get_users_list_bal(page, users_per_page=12, is_staff_only=True):
    users_qs = get_all_users_with_profiles()
    if is_staff_only:
        users_qs = users_qs.filter(is_staff=True)
    paginator = paginate_users(users_qs, page, users_per_page)
    return paginator

def get_user_data_bal(search, status, page, per_page, is_staff_param='all'):
    base_users = filter_users(search, status)
    if is_staff_param == 'true':
        base_users = base_users.filter(is_staff=True)
    elif is_staff_param == 'false':
        base_users = base_users.filter(is_staff=False)
    # else 'all': no filter
    total_users = base_users.count()
    start_index = (page - 1) * per_page
    end_index = min(start_index + per_page, total_users)
    users_page = base_users[start_index:end_index]
    return users_page, total_users

def update_profile_bal(user, full_name, email, profile_picture=None, chat_bot_image=None, chat_bot_img_obj=None, username=None):
    updated = False
    if username and user.username != username:
        user.username = username
        updated = True
    if full_name:
        names = full_name.split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        updated = True
    if email and user.email != email:
        user.email = email
        updated = True
    if updated:
        save_user_dal(user)
    profile = get_user_profile_dal(user)
    profile_updated = False
    if profile_picture:
        profile.profile_picture = profile_picture
        profile_updated = True
    # --- Chat bot image logic ---
    chat_bot_image_path = None
    if chat_bot_image:
        # If it's a file, save and get path; if it's a string/path, use as is
        if hasattr(chat_bot_image, 'name') and hasattr(chat_bot_image, 'chunks'):
            chat_bot_image_path = save_chat_bot_image_file(chat_bot_image)
        else:
            chat_bot_image_path = chat_bot_image
        if chat_bot_img_obj is not None:
            update_content_setting_value(chat_bot_img_obj, chat_bot_image_path)
        else:
            obj, created = get_or_create_content_setting_by_key("chat_bot_image", chat_bot_image_path)
            if not created:
                update_content_setting_value(obj, chat_bot_image_path)
    if profile_updated or updated:
        save_user_profile_dal(profile)
    return user

def toggle_user_status_bal(user_id):
    user = get_user_by_id(user_id)
    profile = get_user_profile_dal(user)
    profile.is_active = not profile.is_active
    save_user_profile_dal(profile)
    return profile.is_active

def delete_user_bal(user_id):
    user = get_user_by_id(user_id)
    if is_user_superuser_dal(user):
        return False, 'Cannot delete superuser'
    delete_user(user)
    return True, None

def change_password_bal(user, current_password, new_password, confirm_password):
    if not all([current_password, new_password, confirm_password]):
        return False, 'All fields are required'
    if new_password != confirm_password:
        return False, 'New password and confirm password do not match'
    if not user.check_password(current_password):
        return False, 'Current password is incorrect'
    set_user_password_dal(user, new_password)
    save_user_dal(user)
    return True, 'Password changed successfully'