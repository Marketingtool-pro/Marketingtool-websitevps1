import os
import requests
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from wowdash_app.utils import log_error_to_file

NOWPAYMENTS_API_KEY = os.environ.get('NOWPAYMENTS_API_KEY', '')

def create_payment(request):
    plan = request.GET.get('plan', 'professional')
    cycle = request.GET.get('cycle', 'yearly')
    price = request.GET.get('price', '99')
    mobile = request.GET.get('mobile', '')
    
    plan_names = {
        'starter': 'Starter Plan',
        'professional': 'Professional Plan', 
        'enterprise': 'Enterprise Plan',
        'basic': 'Basic Plan',
        'standard': 'Standard Plan',
        'premium': 'Premium Plan'
    }
    
    order_id = f'mt_{plan}_{cycle}_{price}'
    
    try:
        response = requests.post(
            'https://api.nowpayments.io/v1/invoice',
            headers={
                'x-api-key': NOWPAYMENTS_API_KEY,
                'Content-Type': 'application/json'
            },
            json={
                'price_amount': float(price),
                'price_currency': 'usd',
                'order_id': order_id,
                'order_description': f'MarketingTool.Pro - {plan_names.get(plan, plan.title())} ({cycle}) - 7 Day Free Trial',
                'ipn_callback_url': 'https://marketingtool.pro/api/payment-webhook/',
                'success_url': 'https://app.marketingtool.pro/dashboard?payment=success',
                'cancel_url': 'https://marketingtool.pro/pricing/'
            }
        )
        
        data = response.json()
        
        if 'invoice_url' in data:
            # Check if mobile - show page instead of redirect
            user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
            is_mobile = 'mobile' in user_agent or 'iphone' in user_agent or 'android' in user_agent
            
            if is_mobile or mobile:
                return render(request, 'pages/mobile_payment.html', {
                    'invoice_url': data['invoice_url'],
                    'invoice_id': data.get('id'),
                    'plan': plan_names.get(plan, plan.title()),
                    'cycle': cycle,
                    'price': price,
                    'title': 'Complete Payment'
                })
            else:
                return HttpResponseRedirect(data['invoice_url'])
        else:
            return JsonResponse({'error': data.get('message', 'Payment creation failed'), 'details': data}, status=400)
            
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)
