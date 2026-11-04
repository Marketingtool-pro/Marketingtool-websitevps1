from django.contrib import messages
from django.shortcuts import redirect, render
from ..utils import log_error_to_file
from Bal.wowdash_app.environmentSettings import get_environment_variables, update_environment_settings

def settings(request):
    if request.method == "POST":
        try:
            update_environment_settings(request.POST)
            messages.success(request, 'Settings updated successfully.', extra_tags="primary")
            return redirect('settings')
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, 'An error occurred. Please try again.', extra_tags="danger")
    env_vars = get_environment_variables()
    return render(request, 'environmentSettings/settings.html', {
        'env_vars': env_vars,
        'title': 'Environment Settings',
        'subtitle': 'General Settings'
    })

def facebookKey(request):
    if request.method == "POST":
        try:
            update_environment_settings(request.POST)
            messages.success(request, 'Settings updated successfully.', extra_tags="primary")
            return redirect('facebookKeySettings')
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, 'An error occurred. Please try again.', extra_tags="danger")
    env_vars = get_environment_variables()
    return render(request, 'environmentSettings/facebookKey.html', {
        'env_vars': env_vars,
        'title': 'Environment Settings',
        'subtitle': 'Facebook Key Settings'
    })

def geminiKey(request):
    if request.method == "POST":
        try:
            update_environment_settings(request.POST)
            messages.success(request, 'Settings updated successfully.', extra_tags="primary")
            return redirect('geminiKeySettings')
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, 'An error occurred. Please try again.', extra_tags="danger")
    env_vars = get_environment_variables()
    return render(request, 'environmentSettings/geminiKey.html', {
        'env_vars': env_vars,
        'title': 'Environment Settings',
        'subtitle': 'Gemini Key Settings'
    })
