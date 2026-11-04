from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout
from wowdash_app.models import ContentSetting
from django.http import JsonResponse
from ..utils import log_error_to_file

from Bal.wowdash_app.user import (
    add_user_bal, get_users_list_bal, get_user_data_bal, update_profile_bal, toggle_user_status_bal, delete_user_bal, change_password_bal
)

def addUser(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            department = request.POST.get('department')
            designation = request.POST.get('designation')
            profile_picture = request.FILES.get('profile_picture')
            if not all([name, email, password, department, designation]):
                messages.error(request, 'All required fields must be filled')
                return redirect('addUser')
            user, error = add_user_bal(name, email, password, department, designation, profile_picture)
            if error:
                messages.error(request, 'An error occurred. Please try again.')
                return redirect('addUser')
            messages.success(request, "User created successfully", extra_tags="primary")
            return redirect('usersList')
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, "An error occurred. Please try again!", extra_tags="warning")
            return redirect('addUser')
    return render(request, 'users/addUser.html', {
        'title': 'Add User',
        'subtitle': 'Add User'
    })

def usersList(request):
    page = request.GET.get('page', 1)
    # Only show admin users if the current user is an admin, else show all users
    if request.user.is_staff:
        users = get_users_list_bal(page, is_staff_only=True)
    else:
        users = get_users_list_bal(page, is_staff_only=False)
    return render(request, 'users/usersList.html', {
        'title': 'Users List',
        'subtitle': 'Users List',
        'script': 'assets/js/custom/users/customUserList.js',
        'users': users
    })


def getUserData(request):
    if request.method == 'GET':
        search = request.GET.get('search', '')
        status = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        is_staff_param = request.GET.get('is_staff', 'all')
        # Pass is_staff_param to BAL
        users_page, total_users = get_user_data_bal(search, status, page, per_page, is_staff_param)
        users_data = []
        for user in users_page:
            try:
                join_date = user.profile.join_date.strftime('%d %b %Y') if user.profile and user.profile.join_date else 'N/A'
                user_data = {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}".strip() or user.username,
                    'email': user.email,
                    'department': user.profile.department if user.profile and user.profile.department else '-',
                    'designation': user.profile.designation if user.profile and user.profile.designation else '-',
                    'join_date': join_date,
                    'status': 'Active' if user.profile and user.profile.is_active else 'Inactive',
                    'profile_picture': user.profile.profile_picture.url if user.profile and user.profile.profile_picture else None,
                    'is_superuser': user.is_superuser
                }
                users_data.append(user_data)
            except Exception:
                continue
        total_pages = (total_users + per_page - 1) // per_page
        if page > total_pages:
            page = total_pages
        elif page < 1:
            page = 1
        return JsonResponse({
            'users': users_data,
            'total_pages': total_pages,
            'current_page': page,
            'total_users': total_users
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def viewProfile(request):
    profile = request.user.profile
    chat_bot_img = ContentSetting.objects.filter(key="chat_bot_image").first()
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            full_name = request.POST.get('name')
            email = request.POST.get('email')
            profile_picture = request.FILES.get('imageUpload')
            chat_bot_image = request.FILES.get('chatBotImage')
            chat_bot_img_obj = chat_bot_img if chat_bot_img else None
            update_profile_bal(request.user, full_name, email, profile_picture, chat_bot_image, chat_bot_img_obj, username=username)
            if chat_bot_image:
                messages.success(request, "Chat Bot image updated!", extra_tags="success")
            messages.success(request, "Profile updated successfully!", extra_tags="success")
            return redirect('viewProfile')
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, "An Error occurred, Try Again!", extra_tags="warning")
            return redirect('viewProfile')
    return render(request, 'users/viewProfile.html', {
        'title': 'View Profile',
        'subtitle': 'View Profile',
        'profile': profile,
        'user': request.user,
        'bot_image': chat_bot_img.value if chat_bot_img else None
    })


def toggleUserStatus(request, user_id):
    if request.method == 'POST':
        try:
            status = toggle_user_status_bal(user_id)
            return JsonResponse({
                'success': True,
                'status': 'Active' if status else 'Inactive',
                'alert': {'type': 'success', 'message': 'User status updated successfully.'}
            })
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'error': 'An error occurred.', 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'error': 'Invalid request method', 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=400)


def deleteUser(request, user_id):
    if request.method == 'POST':
        try:
            success, message = delete_user_bal(user_id)
            if not success:
                return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred. Please try again.'}}, status=400)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'User deleted successfully.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=400)


def changePassword(request):
    if request.method == 'POST':
        try:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            success, message = change_password_bal(request.user, current_password, new_password, confirm_password)
            if success:
                return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'Password changed successfully.'}}, status=200)
            else:
                return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred. Please try again.'}}, status=400)
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=400)

def userLogout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('aiwave-signin')