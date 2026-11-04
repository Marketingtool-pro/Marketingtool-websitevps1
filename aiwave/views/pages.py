from django.shortcuts import render, redirect
import json
from wowdash_app.utils import log_error_to_file, log_and_redirect_to_error_page
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from Bal.aiwave.pages import (
    get_team_data_bal,
    get_content_data_bal,
    get_blog_list_data_bal,
    get_blog_detail_data_bal,
    create_blog_post_bal,
    get_chat_export_data_bal,
    export_chat_sessions_bal,
    get_active_sessions_data_bal,
    terminate_user_session_bal,
    terminate_all_other_sessions_bal,
    get_release_notes_data_bal,
    get_help_faq_data_bal,
    process_help_contact_bal,
    update_user_profile_bal,
    delete_blog_post_bal,
)
from django.urls import reverse
from django.http import JsonResponse, Http404
from django.contrib.auth.models import User
import markdown


def pricing(request):
    return render(request, 'pages/pricing.html', {
        'title': 'Pricing: Starter $29, Pro $59, Growth $99', 'page_description': 'MarketingTool pricing: Starter $29/mo, Pro $59/mo, Growth $99/mo and custom Agency plans, all with a 7-day free trial. AI automation for Google Ads and Meta',
        'subtitle': 'AI Tool'
    })  

def contact(request):
    return render(request, 'pages/contact.html', {
        'title': 'Contact Us — AI Marketing Support & Sales', 'page_description': 'Get in touch with the MarketingTool team — sales inquiries, support, partnerships, or account audits. Direct response within 24 hours on weekdays',
        'subtitle': 'AI Tool'
    })  

def team(request):
    try:
        team_members = get_team_data_bal()
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/team.html', {
            'title': 'Our Team — Building AI Marketing Tools', 'page_description': 'Meet the MarketingTool team — engineers, marketers, and ad operators building the AI Marketing Operating System for Google and Meta Ads',
            'subtitle': 'Meet Our Team',
            'all_members': team_members
        })

def terms(request):
    try:
        terms_content = get_content_data_bal('terms_conditions')
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/termsPolicy.html', {
            'title': 'Terms & Conditions — MarketingTool AI Platform', 'page_description': 'MarketingTool service terms, acceptable use, billing, cancellation, and liability terms. Last updated 2026-04 — plain-English where possible',
            'subtitle': 'AI Tool',
            'terms_content': terms_content
        })

def privacy(request):
    try:
        privacy_content = get_content_data_bal('privacy_conditions')
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/privacyPolicy.html', {
            'title': 'Privacy Policy — MarketingTool AI Marketing Platform', 'page_description': 'How MarketingTool collects, uses and protects your data under GDPR and CCPA: ad account permissions, analytics, data retention and your data subject rights.',
            'subtitle': 'AI Tool',
            'privacy_content': privacy_content
        })


def profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        try:
            full_name = request.POST.get('name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            profile_picture = request.FILES.get('imageUpload')
            
            update_user_profile_bal(request.user, full_name, email, profile_picture, username)
            return redirect('aiwave-profile-details')
        except Exception as e:
            return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/profileDetails.html', {
        'title': 'Your MarketingTool Profile & Account Settings', 'page_description': 'Manage your MarketingTool profile, connected ad accounts, notification preferences, and team access from one dashboard',
        'subtitle': 'View Profile',
        'script': 'js/custom/pages/customProfileDetails.js',
        'profile': profile,
        'user': request.user,
    })

def blog(request):
    """View for listing all blog posts"""
    try:
        search_query = request.GET.get('search', '').strip()
        category = request.GET.get('category', '')
        page = request.GET.get('page')

        context = get_blog_list_data_bal(search_query, category, page)
    except Exception as e:
        return log_and_redirect_to_error_page(e)

    return render(request, 'pages/blog.html', {
        'title': 'Blog — AI, Google & Meta Ads Strategy', 'page_description': 'AI marketing playbooks, Google Ads strategy, Meta Ads experiments, and ad-operations tutorials from the MarketingTool team',
        'mainTitle': 'Our Blog',
        'subtitle': 'AI Tool',
        'script': 'js/custom/pages/customBlog.js',
        'custom_css': 'css/custom/pages/customBlog.css',
        **(context or {})
    })

def blogDetails(request, slug):
    """View for displaying a single blog post"""
    try:
        context = get_blog_detail_data_bal(slug)
        if not context or not context.get('post'):
            raise Http404("Blog post not found")

        # Convert markdown content to HTML if present
        if 'post' in context and hasattr(context['post'], 'content'):
            context['post'].html_content = markdown.markdown(context['post'].content)
        # SEO: inject per-post title and page_description from the post object
        post = context.get('post')
        if post:
            _t = getattr(post, 'title', '') or ''
            if len(_t) > 60:
                _t = _t[:58].rsplit(' ', 1)[0].rstrip(' :,-–—') + '…'
            context['title'] = _t
            desc_source = ''
            if getattr(post, 'excerpt', None):
                desc_source = post.excerpt
            elif getattr(post, 'content', None):
                import re as _re
                desc_source = _re.sub(r'<[^>]+>', '', post.content or '').strip()
            # Meta description target: 140-160 chars
            context['page_description'] = (desc_source if len(desc_source) <= 158 else desc_source[:157].rsplit(' ', 1)[0].rstrip(' ,.;:-–—') + '…') if desc_source else ''
    except Http404:
        raise
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/blogDetails.html', {
        'script': 'js/custom/pages/customBlogDetails.js',
        'custom_css': 'css/custom/pages/customBlogDetails.css',
        **context
        })

@login_required
def createBlog(request):
    """View for creating a new blog post"""
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            content = request.POST.get('content')
            excerpt = request.POST.get('excerpt')
            category = request.POST.get('category')
            tags_input = request.POST.get('tags', '')
            featured_image = request.FILES.get('featured_image')
            
            # Process tags - split by comma and clean
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            # Create the blog post
            blog = create_blog_post_bal(
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=','.join(tags),  # Convert back to string for backward compatibility
                featured_image=featured_image,
                author=request.user
            )
            
            return redirect('aiwave-blog-details', slug=blog.slug)
            
        except Exception as e:
            return log_error_to_file(e)
    
    # Clear any existing messages when just viewing the form
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'pages/createBlog.html', {
        'custom_css': 'css/custom/pages/customCreateBlog.css',
        'script': 'js/custom/pages/customCreateBlog.js',
    })

def chatExports(request):
    if not request.user.is_authenticated:
        return redirect('aiwave-signin')
    
    try:
        bot_modes = get_chat_export_data_bal(request.user)
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/chatExports.html', {
            'title': 'Chat Export — Download Your AI Marketing Conversations', 'page_description': 'Export your AI chat history with MarketingTool — download transcripts, share with your team, or archive campaigns for compliance',
            'subtitle': 'Export your chat conversations',
            'script': 'js/custom/pages/customChatExports.js',
            'bot_modes': bot_modes
        })

@login_required
@require_http_methods(['POST'])
def exportChatSessions(request):
    """Export selected chat sessions"""
    try:
        session_ids = request.POST.getlist('session_ids[]')
        if not session_ids:
            return JsonResponse({
                'status': 'error',
                'message': 'No sessions selected'
            }, status=400)

        export_data = export_chat_sessions_bal(session_ids, request.user)

        return JsonResponse({
            'status': 'success',
            'data': export_data
        })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred.'
        }, status=500)

def plansBilling(request):
    try:
        # Get FAQ data for the pricing page
        faq_data = get_help_faq_data_bal()
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/plansBilling.html', {
            'title': 'Plans & Billing — MarketingTool Subscription Management', 'page_description': 'Manage your MarketingTool subscription, payment methods, invoices, and plan upgrades. Stripe-powered billing with transparent pricing',
            'subtitle': 'AI Tool',
            'faq_categories': faq_data['faq_categories'],
            'faqs_by_category': faq_data['faqs_by_category'],
        })

@login_required
def sessionsPage(request):
    """Render the sessions management page"""
    return render(request, 'pages/sessions.html', {
        'title': 'Active Sessions — MarketingTool Security Center', 'page_description': 'View and manage active login sessions across browsers and devices. Revoke access instantly from any session you do not recognize',
        'subtitle': 'Manage your active sessions',
        'script': 'js/custom/pages/customSessions.js',
    })

@login_required
def getActiveSessions(request):
    """Get all active sessions for the current user"""
    try:
        sessions_data = get_active_sessions_data_bal(request.user, request.session.session_key)
        
        return JsonResponse({
            'status': 'success',
            'sessions': sessions_data
        })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred. Please try again.'
        }, status=500)

@login_required
@require_http_methods(['POST'])
def terminateSession(request):
    """Terminate a specific session"""
    try:
        session_id = request.POST.get('session_id')
        if not session_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Session ID is required'
            }, status=400)

        terminate_user_session_bal(session_id, request.user, request.session.session_key)

        return JsonResponse({
            'status': 'success',
            'message': 'Session terminated successfully'
        })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred.'
        }, status=500)

@login_required
@require_http_methods(['POST'])
def terminateAllSessions(request):
    """Terminate all sessions except the current one"""
    try:
        terminate_all_other_sessions_bal(request.user, request.session.session_key)

        return JsonResponse({
            'status': 'success',
            'message': 'All other sessions terminated successfully'
        })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred.'
        }, status=500)

def releaseNotes(request):
    try:
        release_notes = get_release_notes_data_bal()
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/releaseNotes.html', {
            'title': 'Release Notes — Platform Updates', 'page_description': 'Latest MarketingTool product updates — new AI tools, integrations, performance improvements, and bug fixes shipped weekly',
            'subtitle': 'Release Notes',
            'release_notes': release_notes
        })



def help(request):
    try:
        help_data = get_help_faq_data_bal()
        
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            phone = request.POST.get('phone')
            message = request.POST.get('message')

            try:
                process_help_contact_bal(name, email, subject, phone, message)
                return redirect('aiwave-contact')
            except Exception as e:
                log_error_to_file(e)

    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'pages/help.html', {
            'title': 'Help Center — AI Marketing Support', 'page_description': 'MarketingTool help center — setup guides, troubleshooting, integration docs for Google Ads, Meta, Shopify, and GA4 connections',
            'mainTitle': 'Help Center',
            'subtitle': 'Help & FAQ',
            'custom_css': 'css/custom/pages/customHelp.css',
            'script': 'js/custom/pages/customHelp.js',
            'faq_categories': help_data['faq_categories'],
            'faqs_by_category': help_data['faqs_by_category'],
        })


@login_required
@require_http_methods(["POST"])
def deleteBlog(request, pk):
    """Delete a blog post if the user is the author"""
    delete_blog_post_bal(pk, request.user)
    
    return redirect(reverse('aiwave-blog'))

@csrf_exempt
def n8n_create_blog(request):
    """Endpoint for n8n HTTP node to create a blog post automatically."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    # Locked 2026-10-21: this endpoint had no authentication, so anyone could publish posts.
    # It now requires settings.N8N_BLOG_SECRET (set from the server .env) sent as the X-Webhook-Secret header.
    import hmac
    from django.conf import settings as _settings
    _secret = getattr(_settings, 'N8N_BLOG_SECRET', '') or ''
    if not _secret or not hmac.compare_digest(request.headers.get('X-Webhook-Secret', ''), _secret):
        return JsonResponse({'status': 'error', 'message': 'Forbidden'}, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        title = data.get('title')
        content = data.get('content')
        excerpt = data.get('excerpt', '')
        category = data.get('category', '')
        tags = data.get('tags', '')
        author_username = data.get('author_username')
        featured_image = request.FILES.get('featured_image')
        if not featured_image:
            # Use default image if none provided
            from django.core.files.base import ContentFile
            import os
            default_image_path = os.path.join('media', 'blog/images/default.png')
            try:
                with open(default_image_path, 'rb') as f:
                    image_content = f.read()
                featured_image = ContentFile(image_content, name='default.png')
            except Exception as e:
                print(f"Default image not found at {default_image_path}: {e}")
                featured_image = None

        # Validate required fields
        missing_fields = []
        if not title:
            missing_fields.append('title')
        if not content:
            missing_fields.append('content')
        if not author_username:
            missing_fields.append('author_username')
        if missing_fields:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields', 'missing_fields': missing_fields}, status=400)

        # Get author user
        try:
            author = User.objects.get(username=author_username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Author user not found'}, status=404)

        # Create blog post
        blog = create_blog_post_bal(title, content, excerpt, category, tags, featured_image, author)
        if not blog:
            return JsonResponse({'status': 'error', 'message': 'Failed to create blog post'}, status=500)

        return JsonResponse({'status': 'success', 'slug': blog.slug, 'id': blog.id})
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'}, status=500)


def render_error_page(request, status=404):
    title = 'Page Not Found' if status == 404 else 'Something Went Wrong'
    return render(request, 'pages/404.html', {'title': title}, status=status)

def custom_404_view(request, exception):
    return render_error_page(request, status=404)

def custom_500_view(request):
    return render_error_page(request, status=500)

def error_page(request):
    return render_error_page(request, status=404)

# Tool Landing Pages
def ai_marketing_agents(request):
    return render(request, "pages/tool-ai-marketing-agents.html", {
        "title": "AI Marketing Agents for Ads Automation", "page_description": "Autonomous AI marketing agents run your Google and Meta ad campaigns 24/7 — budget pacing, creative tests, audience expansion without manual clicks.",
        "mainTitle": "AI Marketing Agents",
        "subtitle": "AI Tool"
    })

def ecommerce_tools(request):
    return render(request, "pages/tool-ecommerce.html", {
        "title": "E-commerce & Shopify AI Marketing Tools", "page_description": "Shopify-ready AI marketing suite for product launches, catalog ads, and abandoned cart recovery across Google Shopping, Meta and TikTok.", 
        "mainTitle": "E-commerce & Shopify Tools",
        "subtitle": "AI Tool"
    })

def analytics_platform(request):
    return render(request, "pages/tool-analytics.html", {
        "title": "AI Analytics Platform for Marketers", "page_description": "Unified analytics across Google Ads, Meta, GA4, and Shopify. AI attribution shows which campaigns actually drive profitable revenue.",
        "mainTitle": "Analytics Platform",
        "subtitle": "AI Tool"
    })

def content_writing_tools(request):
    return render(request, "pages/tool-content-writing.html", {
        "title": "AI Content Writing Tools for Marketers", "page_description": "AI copywriting tools for ad headlines, product descriptions, blogs and emails — trained on paid-media-winning copy patterns.",
        "mainTitle": "Content Writing Tools",
        "subtitle": "AI Tool"
    })

def creative_ads_tools(request):
    return render(request, "pages/tool-creative-ads.html", {
        "title": "AI Creative & Ads Tools for Marketers", "page_description": "Generate ad creatives, thumbnails, and video variations in minutes. Built-in testing loop ranks winners on Meta and Google.",
        "mainTitle": "Creative & Ads Tools",
        "subtitle": "AI Tool"
    })

def seo_tools(request):
    return render(request, "pages/tool-seo.html", {
        "title": "AI SEO Tools for Audit, Research & Content", "page_description": "End-to-end AI SEO toolkit: technical audits, keyword research, content briefs and on-page optimization to help your pages rank and win more organic clicks.",
        "mainTitle": "SEO Tools",
        "subtitle": "AI Tool"
    })

def ppc_tools(request):
    return render(request, "pages/tool-ppc.html", {
        "title": "AI PPC Optimization Tools for Google & Meta", "page_description": "Automated bidding rules, negative keyword discovery, creative rotation, and budget pacing for high-ROAS Google and Meta campaigns.",
        "mainTitle": "Optimization & PPC Tools",
        "subtitle": "AI Tool"
    })

# New Company Footer Pages
def how_to_use(request):
    return render(request, "pages/howToUse.html", {
        "title": "How to Use MarketingTool — Setup & Workflows", "page_description": "Complete setup guide — connect Google Ads, Meta, Shopify, and GA4. Walkthrough of every workflow from audit to automation.",
        "mainTitle": "How to use",
        "mainTitle": "AI Marketing Agents",
        "subtitle": "AI Tool"
    })

def roadmap(request):
    return render(request, "pages/roadmap.html", {
        "title": "MarketingTool Product Roadmap 2026", "page_description": "See what's shipping next — TikTok Ads integration, Bing Ads, autonomous creative studio, and new AI agents throughout 2026.",
        "mainTitle": "Roadmap",
        "mainTitle": "AI Marketing Agents",
        "subtitle": "AI Tool"
    })

def guide(request):
    return render(request, "pages/guide.html", {
        "title": "Complete MarketingTool Guide for Marketers", "page_description": "Comprehensive guide for marketers running paid ads at scale: strategies, templates and automation playbooks for Google Ads, Meta Ads, Shopify and GA4.",
        
        "mainTitle": "Guide",
        "subtitle": "AI Tool"
    })

def audit_report(request):
    return render(request, "pages/auditReport.html", {
        "title": "AI Account Audit Report for Google & Meta Ads", "page_description": "Free AI audit of your Google Ads and Meta campaigns — wasted spend, missed opportunities, and 30-day improvement roadmap.",
        "mainTitle": "AI Marketing Agents",
        "subtitle": "AI Tool"
    })

# About Us Page (like madgicx why-madgicx)
def about_us(request):
    return render(request, "pages/about.html", {
        "title": "About MarketingTool – AI Marketing OS for Ads", "page_description": "MarketingTool is an AI Marketing Operating System for Google and Meta Ads — built by ex-ad operators to eliminate manual campaign work.",
        "mainTitle": "Why MarketingTool?",
        "subtitle": "AI Tool"
    })

# Resource Pages Views
def resource_creative_ads(request):
    return render(request, "resources/creative-ads.html", {"title": "AI Creative & Ads Tools Resources — Guides & Examples", "page_description": "Swipe-file and strategy guides for running AI-generated ad creative on Meta and Google — real examples, winning patterns, and prompt templates.", "mainTitle": "Creative & Ads Tools Resources", "subtitle": "AI Tool"})

def resource_ai_agents(request):
    return render(request, "resources/ai-agents.html", {"title": "AI Marketing Agents Resources — Guides & Use Cases", "page_description": "How to deploy autonomous AI marketing agents for ad operations, creative testing, and reporting — use cases from D2C and SaaS teams.", "mainTitle": "AI Marketing Agents Resources", "subtitle": "AI Tool"})

def resource_analytics(request):
    return render(request, "resources/analytics.html", {"title": "AI Analytics Resources — Dashboards & Attribution", "page_description": "Templates for unified paid-media dashboards, attribution setups, and KPI reporting across Google Ads, Meta, GA4, and Shopify.", "mainTitle": "Analytics Resources", "subtitle": "AI Tool"})

def resource_automation(request):
    return render(request, "resources/automation.html", {"title": "AI Marketing Automation Suite for Campaigns", "page_description": "Automate budget pacing, creative rotation, negative-keyword hygiene, and campaign pausing — AI rules that replace manual ad ops.", "mainTitle": "Automation Suite", "subtitle": "AI Tool"})

def resource_audit_tools(request):
    return render(request, "resources/audit-tools.html", {"title": "AI Marketing Audit Tools for Google & Meta", "page_description": "One-click AI audit for Google Ads, Meta, and GA4 accounts — surfaces wasted spend, poor-converting keywords, and missing conversion tracking.", "mainTitle": "Audit Tools", "subtitle": "AI Tool"})

def resource_campaign_hub(request):
    return render(request, "resources/campaign-hub.html", {"title": "Multi-Platform AI Campaign Hub for Marketers", "page_description": "Launch and manage Google, Meta, TikTok, and Bing ad campaigns from a single workspace with AI-driven cross-platform budget allocation.", "mainTitle": "Multi-Platform Campaign Hub", "subtitle": "AI Tool"})

def resource_campaign_mgmt(request):
    return render(request, "resources/campaign-mgmt.html", {"title": "AI Campaign Management for Google & Meta Ads", "page_description": "Manage hundreds of Google Ads and Meta campaigns with AI — automated bidding, audience expansion, and creative refresh on autopilot.", "mainTitle": "Campaign Management", "subtitle": "AI Tool"})

def resource_agentic(request):
    return render(request, "resources/agentic.html", {"title": "Agentic AI Marketing for Autonomous Campaigns", "page_description": "Agentic AI that plans, executes, and optimizes paid-ad campaigns with zero human clicks — the next step beyond rule-based automation.", "mainTitle": "Agentic Marketing", "subtitle": "AI Tool"})

def resource_creative_intel(request):
    return render(request, "resources/creative-intel.html", {"title": "AI Creative Intelligence for Ad Performance", "page_description": "Break down which creatives win and why — AI-powered creative intelligence across Meta and Google so you know what to make next.", "mainTitle": "Creative Intelligence", "subtitle": "AI Tool"})

def resource_content_writing(request):
    return render(request, "resources/content-writing.html", {"title": "Content Writing Resources — AI Copy Templates", "page_description": "Ready-to-use AI copy templates for ad headlines, product pages, cold email, and blog intros — all tested on real campaigns.", "mainTitle": "Content Writing Resources", "subtitle": "AI Tool"})

def resource_management(request):
    return render(request, "resources/management.html", {"title": "AI Marketing Management Tools for Ad Operations", "page_description": "AI management tools for ad ops teams: automated reporting, anomaly detection and campaign QA across Google Ads, Meta and other paid channels in one place.", "mainTitle": "Management Tools", "subtitle": "AI Tool"})

def resource_ppc_research(request):
    return render(request, "resources/ppc-research.html", {"title": "PPC Keyword Research Tools for Google & Meta Ads", "page_description": "AI keyword research for Google Ads and Meta — discover low-CPC opportunities, competitor keywords, and negative-keyword gaps.", "mainTitle": "PPC Research", "subtitle": "AI Tool"})

def resource_ppc_audit(request):
    return render(request, "resources/ppc-audit.html", {"title": "Get Your Free AI PPC Audit for Google & Meta", "page_description": "Free AI-powered PPC audit: connect your Google Ads or Meta account and get a prioritized fix list for wasted spend, keywords and tracking within minutes.", "mainTitle": "Get Your PPC Audit", "subtitle": "AI Tool"})

def resource_test_drive(request):
    return render(request, "resources/test-drive.html", {"title": "Test Drive the AI Marketing Dashboard — Live Demo", "page_description": "See the full MarketingTool dashboard with live data — test-drive every feature before you sign up, no credit card required.", "mainTitle": "Test Drive Dashboard", "subtitle": "AI Tool"})

# Marketing Solutions Views
def solution_email_campaign(request):
    return render(request, "resources/email-campaign.html", {"title": "AI Email Campaign Generator for Marketers", "page_description": "Generate high-converting marketing emails — subject lines, body copy, and segmented variations — with AI trained on winning sequences.", "mainTitle": "Email Campaign", "subtitle": "AI Tool"})

def solution_website_gen(request):
    return render(request, "resources/website-gen.html", {"title": "AI Website Generator for Marketing Landing Pages", "page_description": "Spin up conversion-optimized landing pages in minutes — AI writes, designs, and A/B tests against your existing traffic.", "mainTitle": "Website Generator", "subtitle": "AI Tool"})

def solution_facebook_ads(request):
    return render(request, "resources/facebook-ads.html", {"title": "AI Facebook Ad Generator — Copy & Creative in Minutes", "page_description": "Generate Facebook and Instagram ads — copy, headlines, and visual variants — tuned for your brand, product, and audience in minutes.", "mainTitle": "Facebook Ad Generator", "subtitle": "AI Tool"})

def solution_campaign_builder(request):
    return render(request, "resources/campaign-builder.html", {"title": "Multi-Channel Campaign Builder for Google & Meta", "page_description": "Build cross-channel campaigns in one flow — Google Ads, Meta, Shopping, and email launched together from a single brief.", "mainTitle": "Campaign Builder", "subtitle": "AI Tool"})

def solution_summary_gen(request):
    return render(request, "resources/summary-gen.html", {"title": "AI Marketing Summary Generator for Reports", "page_description": "Turn raw campaign data into client-ready marketing summaries — weekly, monthly, and quarterly reports written by AI in seconds.", "mainTitle": "Summary Generator", "subtitle": "AI Tool"})

def solution_description_gen(request):
    return render(request, "resources/description-gen.html", {"title": "AI Product Description Generator for Shopify & Meta", "page_description": "AI product description generator for Shopify catalogs and Meta product ads — SEO-optimized copy for thousands of SKUs in bulk.", "mainTitle": "Description Generator", "subtitle": "AI Tool"})

def cookiePolicy(request):
    return render(request, 'pages/cookiePolicy.html', {
        'title': 'Cookie Policy — MarketingTool Data & Tracking', 'page_description': 'How MarketingTool uses cookies and tracking technologies — essential, performance, and marketing cookies explained. GDPR compliant',
        'mainTitle': 'Cookie Policy',
    })


def trustVerification(request):
    return render(request, "pages/trustVerification.html", {
        "title": "Trust, Security & Verification — MarketingTool", "page_description": "Our verification credentials, SOC-compliant infrastructure, identity federation, and how we keep your ad accounts and data safe.",
        "mainTitle": "Trust & Verification",
    })

def refundPolicy(request):
    return render(request, "pages/refundPolicy.html", {
        "title": "Refund Policy — MarketingTool AI Marketing Platform", "page_description": "MarketingTool refund policy — full refund within 7 days for monthly plans and 14 days for annual plans, plus cancellation and token terms.",
        "mainTitle": "Refund Policy",
    })
def keywords_search_terms(request):
    return render(request, 'keywords-search-terms.html', {'title': 'Keywords & Search Terms Research for Google & Meta Ads', 'page_description': 'Research high-intent keywords and search terms across Google Ads and Meta — find low-CPC opportunities and negative-keyword gaps', 'mainTitle': 'Keywords & Search Terms', 'subtitle': 'AI Tool'})

def free_tools(request):
    return render(request, "pages/free-tools.html", {"title": "Free AI Marketing Tools for Ads & SEO", "page_description": "Free AI marketing tools — keyword research, ad copy generator, audit reports, and more. No credit card required, no signup wall.", "mainTitle": "Free Marketing Tools", "subtitle": "AI Tool"})


def blog_ai_marketing_agents(request):
    content = '''
    <p>AI Marketing Agents are revolutionizing the way businesses approach digital marketing. These intelligent systems work around the clock to optimize your campaigns, analyze data, and make real-time decisions that improve your ROI.</p>
    
    <h3>What Are AI Marketing Agents?</h3>
    <p>AI Marketing Agents are autonomous software programs that use artificial intelligence to perform marketing tasks. They can analyze customer behavior, predict trends, optimize ad spend, and personalize content at scale.</p>
    
    <h3>Key Benefits</h3>
    <ul>
        <li><strong>24/7 Operation:</strong> AI agents never sleep, constantly monitoring and optimizing your campaigns.</li>
        <li><strong>Data-Driven Decisions:</strong> Make decisions based on real-time data analysis.</li>
        <li><strong>Personalization at Scale:</strong> Deliver personalized experiences to millions of customers.</li>
        <li><strong>Cost Efficiency:</strong> Reduce manual labor and improve marketing ROI.</li>
    </ul>
    
    <h3>How to Get Started</h3>
    <p>Getting started with AI Marketing Agents is easier than you think. MarketingTool provides a suite of AI-powered tools that can help you automate your marketing efforts and achieve better results.</p>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI Marketing Agents for Google & Meta Ads', 'page_description': 'Blog articles on autonomous AI marketing agents — setup guides, use cases, case studies from D2C and SaaS teams running AI ad ops',
        'mainTitle': 'AI Marketing Agents',
        'blog_title': 'AI Marketing Agents',
        'blog_image': 'blog-01.jpg',
        'blog_date': '19 Jan 2026',
        'blog_views': '1,234',
        'blog_category': 'AI Tools',
        'blog_content': content
    })

def blog_ecommerce_tools(request):
    content = '''
    <p>E-commerce and Shopify marketing tools are essential for any online store looking to increase sales and grow their customer base.</p>
    
    <h3>Why E-commerce Tools Matter</h3>
    <p>With the rise of online shopping, having the right marketing tools can make the difference between a struggling store and a thriving business.</p>
    
    <h3>Key Features</h3>
    <ul>
        <li><strong>Product Recommendations:</strong> AI-powered suggestions to increase average order value.</li>
        <li><strong>Abandoned Cart Recovery:</strong> Automated emails to bring back lost customers.</li>
        <li><strong>Inventory Management:</strong> Smart tools to optimize your stock levels.</li>
        <li><strong>Customer Segmentation:</strong> Target the right customers with the right offers.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — E-commerce & Shopify AI Marketing Tools', 'page_description': 'Blog articles on AI marketing for e-commerce and Shopify — catalog ads, cart recovery, product feeds, and checkout optimization',
        'mainTitle': 'E-commerce/Shopify Tools',
        'blog_title': 'E-commerce/Shopify Tools',
        'blog_image': 'blog-02.jpg',
        'blog_date': '18 Jan 2026',
        'blog_views': '987',
        'blog_category': 'E-commerce',
        'blog_content': content
    })

def blog_analytics_platform(request):
    content = '''
    <p>Our Analytics Platform provides comprehensive insights into your marketing performance, helping you make data-driven decisions.</p>
    
    <h3>Real-Time Analytics</h3>
    <p>Track your campaigns in real-time with our powerful dashboard that gives you instant visibility into key metrics.</p>
    
    <h3>Key Metrics We Track</h3>
    <ul>
        <li><strong>Traffic Sources:</strong> Understand where your visitors come from.</li>
        <li><strong>Conversion Rates:</strong> Track how well your campaigns convert.</li>
        <li><strong>Customer Journey:</strong> Map the entire path from awareness to purchase.</li>
        <li><strong>ROI Analysis:</strong> Calculate the return on your marketing investment.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI Analytics Platform & Attribution', 'page_description': 'Blog articles on AI analytics and attribution — unified dashboards across Google Ads, Meta, GA4, and Shopify with AI attribution models',
        'mainTitle': 'Analytics Platform',
        'blog_title': 'Analytics Platform',
        'blog_image': 'blog-03.jpg',
        'blog_date': '17 Jan 2026',
        'blog_views': '856',
        'blog_category': 'Analytics',
        'blog_content': content
    })

def blog_content_writing(request):
    content = '''
    <p>Content Writing Tools powered by AI help you create compelling content faster and more efficiently than ever before.</p>
    
    <h3>AI-Powered Writing</h3>
    <p>Our AI writing assistants can help you create blog posts, social media content, email campaigns, and more in minutes.</p>
    
    <h3>Tools Available</h3>
    <ul>
        <li><strong>Article Rewriter:</strong> Transform existing content into fresh new articles.</li>
        <li><strong>Blog Intro Writer:</strong> Generate engaging introductions that hook readers.</li>
        <li><strong>Content Summarizer:</strong> Condense long articles into key points.</li>
        <li><strong>SEO Content Generator:</strong> Create content optimized for search engines.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI Content Writing Tools for Marketers', 'page_description': 'Blog articles on AI copywriting — ad headlines, product descriptions, blog content, and email copy tested on real paid campaigns',
        'mainTitle': 'Content Writing Tools',
        'blog_title': 'Content Writing Tools',
        'blog_image': 'blog-04.jpg',
        'blog_date': '16 Jan 2026',
        'blog_views': '1,543',
        'blog_category': 'Writing',
        'blog_content': content
    })

def blog_creative_ads(request):
    content = '''
    <p>Creative & Ads Tools help you design stunning advertisements that capture attention and drive conversions.</p>
    
    <h3>Design Made Easy</h3>
    <p>Create professional-quality ads without any design experience using our AI-powered creative tools.</p>
    
    <h3>Ad Formats Supported</h3>
    <ul>
        <li><strong>Facebook Ads:</strong> Create scroll-stopping social media ads.</li>
        <li><strong>Google Display Ads:</strong> Design banner ads that convert.</li>
        <li><strong>Video Ads:</strong> Generate video content for any platform.</li>
        <li><strong>Email Graphics:</strong> Beautiful visuals for email campaigns.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI Creative & Ads Tools for Performance Marketing', 'page_description': 'Blog articles on AI-generated ad creative — image generation, video ads, creative testing, and what actually wins on Meta and Google',
        'mainTitle': 'Creative & Ads Tools',
        'blog_title': 'Creative & Ads Tools',
        'blog_image': 'blog-05.jpg',
        'blog_date': '15 Jan 2026',
        'blog_views': '765',
        'blog_category': 'Ads',
        'blog_content': content
    })

def blog_seo_tools(request):
    content = '''
    <p>SEO Tools help you optimize your website for search engines and drive more organic traffic to your site.</p>
    
    <h3>Comprehensive SEO Suite</h3>
    <p>Our SEO tools cover everything from keyword research to technical SEO audits.</p>
    
    <h3>Features</h3>
    <ul>
        <li><strong>Keyword Research:</strong> Find the best keywords for your content.</li>
        <li><strong>On-Page SEO:</strong> Optimize your pages for better rankings.</li>
        <li><strong>Technical SEO:</strong> Fix issues that hurt your search visibility.</li>
        <li><strong>Competitor Analysis:</strong> See what your competitors are doing.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI SEO Tools, Research & Audit Strategies', 'page_description': 'Blog articles on AI SEO: technical audits, keyword research, content briefs and on-page optimization, with step-by-step guides from the MarketingTool team.',
        'mainTitle': 'SEO Tools',
        'blog_title': 'SEO Tools',
        'blog_image': 'blog-06.jpg',
        'blog_date': '14 Jan 2026',
        'blog_views': '2,341',
        'blog_category': 'SEO',
        'blog_content': content
    })

def blog_ppc_tools(request):
    content = '''
    <p>PPC & Optimization Tools help you maximize your paid advertising ROI with smart automation and analytics.</p>
    
    <h3>Smart PPC Management</h3>
    <p>Automate your PPC campaigns and let AI optimize your bids, budgets, and targeting.</p>
    
    <h3>Tools Included</h3>
    <ul>
        <li><strong>Bid Management:</strong> Automated bidding for maximum ROI.</li>
        <li><strong>Budget Optimization:</strong> Allocate spend to best-performing campaigns.</li>
        <li><strong>A/B Testing:</strong> Test ad variations to find winners.</li>
        <li><strong>Performance Reports:</strong> Detailed analytics on campaign performance.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — AI PPC Tools for Google & Meta Ads Optimization', 'page_description': 'Blog articles on AI PPC optimization — automated bidding, negative keyword discovery, creative rotation, and budget pacing',
        'mainTitle': 'Optimization & PPC Tools',
        'blog_title': 'Optimization & PPC Tools',
        'blog_image': 'blog-07.jpg',
        'blog_date': '13 Jan 2026',
        'blog_views': '1,876',
        'blog_category': 'PPC',
        'blog_content': content
    })

def blog_campaign_hub(request):
    content = '''
    <p>Campaign Hub is your central command center for managing all your marketing campaigns across multiple channels.</p>
    
    <h3>Multi-Channel Management</h3>
    <p>Manage email, social, PPC, and content campaigns all from one unified dashboard.</p>
    
    <h3>Key Capabilities</h3>
    <ul>
        <li><strong>Campaign Planning:</strong> Plan and schedule campaigns in advance.</li>
        <li><strong>Cross-Channel Tracking:</strong> See performance across all channels.</li>
        <li><strong>Team Collaboration:</strong> Work together with your marketing team.</li>
        <li><strong>Automated Workflows:</strong> Set up triggers and automated actions.</li>
    </ul>
    '''
    return render(request, 'pages/blog-detail.html', {
        'title': 'Blog — Multi-Platform AI Campaign Hub', 'page_description': 'Blog articles on running multi-channel ad campaigns — Google, Meta, TikTok, and Bing unified with AI-driven budget allocation',
        'mainTitle': 'Campaign Hub',
        'blog_title': 'Campaign Hub',
        'blog_image': 'blog-08.jpg',
        'blog_date': '12 Jan 2026',
        'blog_views': '654',
        'blog_category': 'Marketing',
        'blog_content': content
    })

# Free Tools - Dedicated Landing Pages (placeholders - to be updated)
def free_tool_google_ads(request):
    return render(request, 'pages/free-tool-google-ads.html', {'title': 'Free Google Ads Performance Grader & AI Audit', 'page_description': 'Free Google Ads audit — connect your account and get AI-generated insights on wasted spend, keyword gaps, and quality score improvements'})

def free_tool_facebook_ads(request):
    return render(request, 'pages/free-tool-facebook-ads.html', {'title': 'Free Facebook Ads Performance Grader & AI Audit', 'page_description': 'Free Facebook Ads audit — analyze Meta campaigns, ROAS by creative, audience performance, and get AI recommendations to boost results'})

def free_tool_website(request):
    return render(request, 'pages/free-tool-website.html', {'title': 'Free Website Grader — AI SEO & Speed Audit', 'page_description': 'Free website audit — AI analyzes your SEO, page speed, Core Web Vitals, and conversion elements. Get a prioritized 30-day improvement plan'})

def deleteAccount(request):
    return render(request, 'pages/deleteAccount.html', {
        'title': 'Delete Account',
        'subtitle': 'Account Deletion'
    })
