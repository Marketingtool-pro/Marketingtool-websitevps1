from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ..utils import log_error_to_file, log_and_redirect_to_error_page
from Bal.wowdash_app.dashboard import get_dashboard_data, toggle_user_status_business, get_statistics_data

@login_required
@require_POST
def toggleUserStatus(request, user_id):
    if not request.user.is_superuser:
        log_error_to_file(Exception('Permission denied.'))
        return JsonResponse({'error': 'Permission denied', 'alert': {'type': 'danger', 'message': 'Permission denied.'}}, status=403)
    try:
        result = toggle_user_status_business(user_id)
        return JsonResponse({
            'success': result['success'],
            'status': result['status'],
            'alert': {'type': 'success', 'message': 'User status updated successfully.'}
        })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred.', 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)

@login_required
def index(request):
    try:
        dashboard_data = get_dashboard_data()
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'dashboard/index.html',{
            'title': 'Dashboard',
            'subtitle': 'AI',
            'script' : 'assets/js/homeOneChart.js',
            **dashboard_data
        })

@login_required
def getStats(request):
    """Unified endpoint for getting various statistics"""
    try:
        stat_type = request.GET.get('type', 'sales')
        period = request.GET.get('period', 'today')
        data = get_statistics_data(stat_type, period)
        return JsonResponse(data)
    except ValueError as e:
        return JsonResponse({'error': 'Invalid request.', 'alert': {'type': 'danger', 'message': 'Invalid request.'}}, status=400)
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred.', 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500) 