import requests
import json
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from wowdash_app.models import EnvVar, SocialAccount
from wowdash_app.utils import log_error_to_file

def get_facebook_credentials():
    try:
        app_id = EnvVar.objects.get(key='FACEBOOK_APP_ID').value
        app_secret = EnvVar.objects.get(key='FACEBOOK_APP_SECRET').value
        return app_id, app_secret
    except:
        return None, None

@login_required
def facebook_connect(request):
    """Start Facebook OAuth flow"""
    app_id, app_secret = get_facebook_credentials()
    if not app_id:
        return JsonResponse({'error': 'Facebook credentials not configured'}, status=400)
    
    redirect_uri = 'https://marketingtool.pro/aiwave/admin/social/facebook/callback/'
    scope = 'pages_show_list,pages_read_engagement,pages_manage_posts,instagram_basic,instagram_content_publish,business_management'
    
    auth_url = f'https://www.facebook.com/v18.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}&response_type=code'
    
    return HttpResponseRedirect(auth_url)

@login_required
def facebook_callback(request):
    """Handle Facebook OAuth callback"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return render(request, 'wowdash/features/social_callback.html', {
            'error': request.GET.get('error_description', 'Authorization failed')
        })
    
    if not code:
        return render(request, 'wowdash/features/social_callback.html', {
            'error': 'No authorization code received'
        })
    
    app_id, app_secret = get_facebook_credentials()
    redirect_uri = 'https://marketingtool.pro/aiwave/admin/social/facebook/callback/'
    
    # Exchange code for access token
    token_url = f'https://graph.facebook.com/v18.0/oauth/access_token?client_id={app_id}&redirect_uri={redirect_uri}&client_secret={app_secret}&code={code}'
    
    response = requests.get(token_url)
    data = response.json()
    
    if 'error' in data:
        return render(request, 'wowdash/features/social_callback.html', {
            'error': data['error'].get('message', 'Token exchange failed')
        })
    
    access_token = data.get('access_token')
    
    # Get long-lived token
    long_token_url = f'https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={access_token}'
    long_response = requests.get(long_token_url)
    long_data = long_response.json()
    long_token = long_data.get('access_token', access_token)
    
    # Get user's pages
    pages_url = f'https://graph.facebook.com/v18.0/me/accounts?access_token={long_token}'
    pages_response = requests.get(pages_url)
    pages_data = pages_response.json()
    
    connected_accounts = []
    
    for page in pages_data.get('data', []):
        page_id = page['id']
        page_name = page['name']
        page_token = page['access_token']
        
        # Save/Update Facebook Page
        fb_account, created = SocialAccount.objects.update_or_create(
            platform='facebook',
            account_id=page_id,
            defaults={
                'account_name': page_name,
                'access_token': page_token,
                'is_active': True
            }
        )
        connected_accounts.append({'platform': 'Facebook Page', 'name': page_name})
        
        # Check for Instagram Business Account
        ig_url = f'https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token={page_token}'
        ig_response = requests.get(ig_url)
        ig_data = ig_response.json()
        
        if 'instagram_business_account' in ig_data:
            ig_id = ig_data['instagram_business_account']['id']
            
            # Get Instagram username
            ig_info_url = f'https://graph.facebook.com/v18.0/{ig_id}?fields=username,name&access_token={page_token}'
            ig_info = requests.get(ig_info_url).json()
            ig_username = ig_info.get('username', 'instagram')
            
            # Save Instagram account
            ig_account, created = SocialAccount.objects.update_or_create(
                platform='instagram',
                account_id=ig_id,
                defaults={
                    'account_name': ig_username,
                    'access_token': page_token,
                    'is_active': True
                }
            )
            connected_accounts.append({'platform': 'Instagram', 'name': ig_username})
    
    return render(request, 'wowdash/features/social_callback.html', {
        'success': True,
        'accounts': connected_accounts
    })

@login_required
@csrf_exempt
def post_to_facebook(request):
    """Post content to Facebook Page"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        account_id = data.get('account_id')
        message = data.get('message')
        image_url = data.get('image_url')
        
        account = SocialAccount.objects.get(id=account_id, platform='facebook')
        
        if image_url:
            # Post with image
            url = f'https://graph.facebook.com/v18.0/{account.account_id}/photos'
            params = {
                'url': image_url,
                'caption': message,
                'access_token': account.access_token
            }
        else:
            # Post text only
            url = f'https://graph.facebook.com/v18.0/{account.account_id}/feed'
            params = {
                'message': message,
                'access_token': account.access_token
            }
        
        response = requests.post(url, data=params)
        result = response.json()
        
        if 'error' in result:
            return JsonResponse({'error': result['error'].get('message')}, status=400)
        
        return JsonResponse({'success': True, 'post_id': result.get('id')})
        
    except SocialAccount.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)

@login_required
@csrf_exempt
def post_to_instagram(request):
    """Post content to Instagram"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
        account_id = data.get('account_id')
        caption = data.get('caption')
        image_url = data.get('image_url')
        
        if not image_url:
            return JsonResponse({'error': 'Instagram requires an image'}, status=400)
        
        account = SocialAccount.objects.get(id=account_id, platform='instagram')
        
        # Step 1: Create media container
        container_url = f'https://graph.facebook.com/v18.0/{account.account_id}/media'
        container_params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': account.access_token
        }
        
        container_response = requests.post(container_url, data=container_params)
        container_result = container_response.json()
        
        if 'error' in container_result:
            return JsonResponse({'error': container_result['error'].get('message')}, status=400)
        
        creation_id = container_result.get('id')
        
        # Step 2: Publish the container
        publish_url = f'https://graph.facebook.com/v18.0/{account.account_id}/media_publish'
        publish_params = {
            'creation_id': creation_id,
            'access_token': account.access_token
        }
        
        publish_response = requests.post(publish_url, data=publish_params)
        publish_result = publish_response.json()
        
        if 'error' in publish_result:
            return JsonResponse({'error': publish_result['error'].get('message')}, status=400)
        
        return JsonResponse({'success': True, 'post_id': publish_result.get('id')})
        
    except SocialAccount.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'An error occurred. Please try again.'}, status=500)

@login_required
def social_accounts_status(request):
    """Get status of all connected social accounts"""
    accounts = SocialAccount.objects.filter(is_active=True)
    result = []
    
    for account in accounts:
        status = {'id': account.id, 'platform': account.platform, 'name': account.account_name, 'connected': bool(account.access_token)}
        
        # Verify token is still valid
        if account.access_token and account.platform in ['facebook', 'instagram']:
            verify_url = f'https://graph.facebook.com/v18.0/me?access_token={account.access_token}'
            response = requests.get(verify_url)
            status['token_valid'] = 'error' not in response.json()
        else:
            status['token_valid'] = False
        
        result.append(status)
    
    return JsonResponse({'accounts': result})
