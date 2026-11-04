from django.contrib import messages
from django.shortcuts import redirect, render
from ..utils import log_error_to_file
from Bal.wowdash_app.siteMetaSettings import get_site_settings, update_site_settings

CATEGORY_CONFIG = {
    'general': {
        'keys': ['site_name', 'site_description', 'site_logo', 'favicon_png', 'small_logo'],
        'template': 'siteMetaSettings/GeneralSiteSettings.html',
        'url_name': 'generalSiteSettings',
        'title': 'General Site Settings',
    },
    'contact': {
        'keys': ['company_address', 'contact_email', 'contact_phone'],
        'template': 'siteMetaSettings/contactInformation.html',
        'url_name': 'contactInformationSettings',
        'title': 'Contact Information',
    },
    'social': {
        'keys': ['social_facebook', 'social_linkedin', 'social_twitter'],
        'template': 'siteMetaSettings/socialMediaLinks.html',
        'url_name': 'socialMediaLinksSettings',
        'title': 'Social Media Links',
    },
}

def settingsCategoryView(request, category):
    config = CATEGORY_CONFIG[category]
    if request.method == "POST":
        try:
            files = request.FILES if category == 'general' else None
            success = update_site_settings(request.POST, files)
            if success:
                messages.success(request, f'{config["title"]} updated successfully.', extra_tags="primary")
            else:
                messages.error(request, 'Failed to update settings. Please try again.', extra_tags="danger")
            return redirect(config['url_name'])
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, 'An error occurred. Please try again.', extra_tags="danger")
    
    # Don't pass meta_vars since context processor provides it
    return render(request, config['template'], {
        'title': config['title'],
    })

# Individual views for each category

def generalSettings(request):
    return settingsCategoryView(request, 'general')

def contactInformationSettings(request):
    return settingsCategoryView(request, 'contact')

def socialMediaLinksSettings(request):
    return settingsCategoryView(request, 'social')
