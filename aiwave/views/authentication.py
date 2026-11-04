from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.template.loader import render_to_string
from wowdash_app.utils import log_error_to_file
from django.contrib import messages
from django.conf import settings
from Bal.aiwave.pages import create_session_record_bal
from Bal.aiwave.authentication import (
    validate_signin_data_bal,
    process_user_signin_bal,
    validate_signup_data_bal,
    check_signup_duplicates_bal,
    process_user_signup_bal,
    validate_password_for_deletion_bal,
    process_account_deletion_bal,
    cleanup_user_session_bal,
    get_user_redirect_url_bal,
    process_password_reset_bal,
    get_user_and_otp_bal,
    send_otp_email_bal,
    get_otp_from_request_bal,
    validate_otp_bal,
    validate_passwords_bal
)
from wowdash_app import utils


def signin(request):
    field_errors = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            if not email:
                field_errors['emailError'] = 'Email is required.'
            if not password:
                field_errors['passwordError'] = 'Password is required.'
            if not field_errors:
                # Validate input data
                validate_signin_data_bal(email, password)
                # Process user signin
                try:
                    user = process_user_signin_bal(email, password)
                except Exception as e:
                    msg = str(e)
                    if 'email' in msg.lower():
                        field_errors['emailError'] = msg
                    elif 'password' in msg.lower():
                        field_errors['passwordError'] = msg
                    else:
                        field_errors['emailError'] = msg
                if not field_errors and user is not None and user.is_authenticated:
                    # Ensure session is saved before login
                    if not request.session.session_key:
                        request.session.save()

                    # Login the user with explicit backend
                    login(request, user, backend='wowdash_app.auth.CustomAuthBackend')

                    # Force session save
                    request.session.save()

                    # Create session record after successful login
                    try:
                        cleanup_user_session_bal(request.session.session_key)
                        create_session_record_bal(request, user)
                    except Exception as e:
                        log_error_to_file(e)
                    # Get the next URL from the request
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    # Get redirect URL based on user role
                    redirect_url = get_user_redirect_url_bal(user)
                    return redirect(redirect_url)
        except Exception as e:
            log_error_to_file(e)
            field_errors['emailError'] = 'An error occurred. Please try again.'
    return render(request, 'pages/signin.html', {
        'field_errors': field_errors,
        'title': 'Sign In to MarketingTool — AI Marketing Platform',
        'subtitle': 'AI Tool',
        'script': 'js\custom\pop_up_model\otpPasswordModel.js'
    })


def signup(request):
    field_errors = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        try:
            if not username:
                field_errors['usernameError'] = 'Username is required.'
            if not email:
                field_errors['emailError'] = 'Email is required.'
            if not password:
                field_errors['passwordError'] = 'Password is required.'
            if password != confirm_password:
                field_errors['confirmPasswordError'] = 'Passwords do not match.'

            # Only proceed if no field errors
            if not field_errors:
                # Validate input data
                validate_signup_data_bal(username, email, password)
                # Check for duplicates
                try:
                    check_signup_duplicates_bal(username, email)
                except Exception as e:
                    msg = str(e)
                    if 'Username' in msg:
                        field_errors['usernameError'] = msg
                    elif 'Email' in msg:
                        field_errors['emailError'] = msg
                    else:
                        field_errors['usernameError'] = msg
                if not field_errors:
                    # Process user signup
                    user = process_user_signup_bal(username, email, password)
                    if user is not None and user.is_authenticated:
                        # Login the user with explicit backend
                        login(request, user, backend='wowdash_app.auth.CustomAuthBackend')
                        return redirect('aiwave-index')
                    else:
                        field_errors['usernameError'] = 'Failed to create user account. Please try again.'
        except Exception as e:
            log_error_to_file(e)
            field_errors['usernameError'] = 'An error occurred. Please try again.'
    return render(request, 'pages/signup.html', {
        'field_errors': field_errors,
        'title': 'Sign Up for MarketingTool — 7-Day Free Trial',
        'subtitle': 'AI Tool'
    })

def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('aiwave-signin')


def deleteUserProfile(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        
        try:
            # Validate password for deletion
            validate_password_for_deletion_bal(request.user, password)
            
            # Process account deletion
            process_account_deletion_bal(request.user)
            
            # Logout the user
            logout(request)
            
            return JsonResponse({
                'success': True
            })
            
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=405)


def forgotPassword(request):

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    status = None
    error = None

    if request.method == "POST":
        # Step 1: Email Submission (Send OTP)
        if 'email' in request.POST and 'otp' not in request.POST and 'new_password' not in request.POST:
            try:
                success, result = process_password_reset_bal(request)
                if success:
                    email = request.POST.get('email')
                    user = get_user_and_otp_bal(email)[0]
                    try:
                        send_otp_email_bal(
                            user=user,
                            otp=result,
                            email_template='emails/otp_email.html',
                            subject='Password Reset OTP',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                        )
                        utils.set_reset_email(user.email, request)
                        is_resend = request.POST.get('resend') == 'true'
                        if is_resend:
                            messages.success(request, 'New OTP has been sent to your email.', extra_tags="primary")
                        else:
                            messages.success(request, 'OTP sent to your email. Please wait...', extra_tags="primary")
                        status = 'otp_sent'
                    except Exception as e:
                        log_error_to_file(e)
                        status = 'error'
                        error = 'Failed to send OTP. Please try again later.'
                else:
                    messages.error(request, result, extra_tags="danger")
                    status = 'error'
                    error = result
            except Exception as e:
                log_error_to_file(e)
                messages.error(request, 'An error occurred, Please Try Again.', extra_tags="danger")
                status = 'error'
                error = 'An error occurred, Please Try Again.'

        # Step 2: OTP Verification
        elif 'otp' in request.POST and 'new_password' not in request.POST:
            reset_email = utils.get_reset_email(request)
            if not reset_email:
                messages.error(request, "Session expired. Please try again.", extra_tags="danger")
                status = 'error'
                error = 'Session expired. Please try again.'
            else:
                try:
                    otp_input = get_otp_from_request_bal(request)
                    user, userotp = get_user_and_otp_bal(reset_email)
                    if user is None or userotp is None:
                        messages.error(request, "User or OTP record not found.", extra_tags="danger")
                        status = 'error'
                        error = 'User or OTP record not found.'
                    else:
                        success, message = validate_otp_bal(userotp, otp_input)
                        if success:
                            messages.success(request, message, extra_tags="primary")
                            request.session['otp_verified'] = True
                            status = 'otp_verified'
                        else:
                            messages.error(request, message, extra_tags="danger")
                            status = 'error'
                            error = message
                except Exception as e:
                    log_error_to_file(e)
                    messages.error(request, "User or OTP record not found.", extra_tags="danger")
                    status = 'error'
                    error = 'User or OTP record not found.'

        # Step 3: Password Reset
        elif 'new_password' in request.POST and 'confirm_password' in request.POST:
            try:
                success, message = validate_passwords_bal(request)
                if success:
                    messages.success(request, message, extra_tags="primary")
                    status = 'password_reset'
                else:
                    messages.error(request, message, extra_tags="danger")
                    status = 'error'
                    error = message
            except Exception as e:
                log_error_to_file(e)
                messages.error(request, "An error occurred during password reset.", extra_tags="danger")
                status = 'error'
                error = 'An error occurred during password reset.'

        if is_ajax:
            alerts_html = render_to_string('components/flotingalert.html', request=request)
            return JsonResponse({
                'status': status,
                'alerts_html': alerts_html,
                'error': error
            })
        else:
            return render(request, 'authentication/forgotPassword.html')

    return render(request, 'authentication/forgotPassword.html')


