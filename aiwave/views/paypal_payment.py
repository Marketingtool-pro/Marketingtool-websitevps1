import requests
import base64
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from wowdash_app.utils import log_error_to_file

# Marketingtool App - Live credentials
PAYPAL_CLIENT_ID = 'AYFUYdfZzHqCDGBcvaW07oHrt30WLy-fxD3tMb4lCJOCOOkeQ3V4Vrp1HbLZaD_KbXnGoszzgzWAgdXR'
PAYPAL_SECRET = 'EPPxEPlQ419LCHSMFi8XoJs7yqUSsHuyUTQWeMq7fJcoDpEo3L1-Zfb_FeDMBvBPzRiEPo1LllCPrbPF'
PAYPAL_API = 'https://api-m.paypal.com'

def get_paypal_token():
    auth = base64.b64encode(f'{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}'.encode()).decode()
    response = requests.post(
        f'{PAYPAL_API}/v1/oauth2/token',
        headers={
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        data='grant_type=client_credentials'
    )
    return response.json().get('access_token')

def create_paypal_order(request):
    plan = request.GET.get('plan', 'professional')
    cycle = request.GET.get('cycle', 'yearly')
    price = request.GET.get('price', '99')
    
    plan_names = {
        'starter': 'Starter Plan',
        'professional': 'Professional Plan', 
        'enterprise': 'Enterprise Plan',
        'basic': 'Basic Plan',
        'standard': 'Standard Plan',
        'premium': 'Premium Plan'
    }
    
    try:
        token = get_paypal_token()
        if not token:
            return JsonResponse({'error': 'Could not get PayPal token'}, status=400)
        
        response = requests.post(
            f'{PAYPAL_API}/v2/checkout/orders',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            json={
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'amount': {
                        'currency_code': 'USD',
                        'value': price
                    },
                    'description': f'MarketingTool.Pro - {plan_names.get(plan, plan.title())} ({cycle})'
                }],
                'application_context': {
                    'brand_name': 'MarketingTool.Pro',
                    'landing_page': 'BILLING',
                    'user_action': 'PAY_NOW',
                    'return_url': 'https://app.marketingtool.pro/dashboard?payment=success',
                    'cancel_url': 'https://marketingtool.pro/pricing/'
                }
            }
        )
        
        data = response.json()
        
        for link in data.get('links', []):
            if link.get('rel') == 'approve':
                return HttpResponseRedirect(link['href'])
        
        return JsonResponse({'error': 'Could not create PayPal order', 'details': data}, status=400)
        
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)
