"""
New Features Views for wowdash_app
- Media Library
- Social Media Scheduler
- AI Blog Generator
- Analytics Dashboard
- Email Newsletter
- Personal AI Assistant (Claude Opus 4.5)
"""

import json
import os
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.utils import timezone
from django.conf import settings
from ..models import (
    MediaFile, SocialAccount, ScheduledPost,
    AIBlogDraft, WebsiteAnalytics, NewsletterSubscriber,
    NewsletterCampaign, AssistantConversation, AssistantMessage
)
from ..auth import admin_required


# ============================================
# MEDIA LIBRARY
# ============================================

@login_required
@admin_required
def media_library(request):
    """Display media library"""
    media_type = request.GET.get('type', 'all')

    if media_type == 'all':
        media_files = MediaFile.objects.all()
    else:
        media_files = MediaFile.objects.filter(media_type=media_type)

    paginator = Paginator(media_files, 24)
    page = request.GET.get('page', 1)
    files = paginator.get_page(page)

    stats = {
        'total': MediaFile.objects.count(),
        'images': MediaFile.objects.filter(media_type='image').count(),
        'videos': MediaFile.objects.filter(media_type='video').count(),
        'documents': MediaFile.objects.filter(media_type='document').count(),
    }

    return render(request, 'wowdash/features/media_library.html', {
        'files': files,
        'stats': stats,
        'current_type': media_type,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def media_upload(request):
    """Handle media upload"""
    if request.FILES.get('file'):
        uploaded_file = request.FILES['file']

        # Determine media type
        content_type = uploaded_file.content_type
        if content_type.startswith('image/'):
            media_type = 'image'
        elif content_type.startswith('video/'):
            media_type = 'video'
        elif content_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            media_type = 'document'
        else:
            media_type = 'other'

        media = MediaFile.objects.create(
            title=request.POST.get('title', uploaded_file.name),
            file=uploaded_file,
            media_type=media_type,
            file_size=uploaded_file.size,
            alt_text=request.POST.get('alt_text', ''),
            description=request.POST.get('description', ''),
            uploaded_by=request.user,
        )

        return JsonResponse({'success': True, 'id': media.id, 'url': media.file.url})

    return JsonResponse({'success': False, 'error': 'No file provided'})


@login_required
@admin_required
@require_http_methods(["DELETE"])
def media_delete(request, media_id):
    """Delete media file"""
    media = get_object_or_404(MediaFile, id=media_id)
    media.file.delete()
    media.delete()
    return JsonResponse({'success': True})


# ============================================
# SOCIAL MEDIA SCHEDULER
# ============================================

@login_required
@admin_required
def social_scheduler(request):
    """Display social media scheduler"""
    posts = ScheduledPost.objects.all()[:50]
    accounts = SocialAccount.objects.filter(is_active=True)

    # Calendar data for the current month
    today = timezone.now().date()
    start_of_month = today.replace(day=1)

    scheduled_posts = ScheduledPost.objects.filter(
        scheduled_time__gte=start_of_month,
        status__in=['scheduled', 'published']
    ).values('scheduled_time', 'title', 'status')

    calendar_data = {}
    for post in scheduled_posts:
        date_str = post['scheduled_time'].strftime('%Y-%m-%d')
        if date_str not in calendar_data:
            calendar_data[date_str] = []
        calendar_data[date_str].append({
            'title': post['title'],
            'status': post['status'],
            'time': post['scheduled_time'].strftime('%H:%M')
        })

    stats = {
        'scheduled': ScheduledPost.objects.filter(status='scheduled').count(),
        'published': ScheduledPost.objects.filter(status='published').count(),
        'drafts': ScheduledPost.objects.filter(status='draft').count(),
    }

    return render(request, 'wowdash/features/social_scheduler.html', {
        'posts': posts,
        'accounts': accounts,
        'calendar_data': json.dumps(calendar_data),
        'stats': stats,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def social_post_create(request):
    """Create a new scheduled post"""
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    post = ScheduledPost.objects.create(
        title=data.get('title'),
        content=data.get('content'),
        scheduled_time=data.get('scheduled_time'),
        status=data.get('status', 'draft'),
        created_by=request.user,
    )

    # Add platforms
    platform_ids = data.get('platforms', [])
    if platform_ids:
        post.platforms.set(platform_ids)

    return JsonResponse({'success': True, 'id': post.id})


@login_required
@admin_required
@require_http_methods(["DELETE"])
def social_post_delete(request, post_id):
    """Delete scheduled post"""
    post = get_object_or_404(ScheduledPost, id=post_id)
    post.delete()
    return JsonResponse({'success': True})


@login_required
@admin_required
@require_http_methods(["POST"])
def social_account_add(request):
    """Add social media account"""
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    account = SocialAccount.objects.create(
        platform=data.get('platform'),
        account_name=data.get('account_name'),
        account_id=data.get('account_id', ''),
        access_token=data.get('access_token', ''),
    )

    return JsonResponse({'success': True, 'id': account.id})


# ============================================
# AI BLOG GENERATOR
# ============================================

@login_required
@admin_required
def ai_blog_generator(request):
    """Display AI blog generator"""
    drafts = AIBlogDraft.objects.all()[:20]

    stats = {
        'total': AIBlogDraft.objects.count(),
        'published': AIBlogDraft.objects.filter(status='published').count(),
        'drafts': AIBlogDraft.objects.filter(status='draft').count(),
    }

    return render(request, 'wowdash/features/ai_blog_generator.html', {
        'drafts': drafts,
        'stats': stats,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def ai_blog_generate(request):
    """Generate blog using AI"""
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    topic = data.get('topic')
    keywords = data.get('keywords', '')
    tone = data.get('tone', 'professional')

    # Create draft record
    draft = AIBlogDraft.objects.create(
        topic=topic,
        keywords=keywords,
        tone=tone,
        status='generating',
        created_by=request.user,
    )

    # Generate content using Gemini
    try:
        from ..utils import generate_blog_content
        result = generate_blog_content(topic, keywords, tone)

        draft.generated_title = result.get('title', topic)
        draft.generated_content = result.get('content', '')
        draft.generated_meta = result.get('meta', '')
        draft.status = 'draft'
        draft.save()

        return JsonResponse({
            'success': True,
            'id': draft.id,
            'title': draft.generated_title,
            'content': draft.generated_content,
        })
    except Exception as e:
        draft.status = 'draft'
        draft.generated_content = f"Error generating content: {str(e)}"
        draft.save()
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@admin_required
@require_http_methods(["DELETE"])
def ai_blog_delete(request, draft_id):
    """Delete AI draft"""
    draft = get_object_or_404(AIBlogDraft, id=draft_id)
    draft.delete()
    return JsonResponse({'success': True})


# ============================================
# ANALYTICS DASHBOARD
# ============================================

@login_required
@admin_required
def analytics_dashboard(request):
    """Display analytics dashboard"""
    from django.contrib.auth.models import User
    from ..models import ChatSession, ChatMessage

    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    # User stats
    total_users = User.objects.count()
    new_users_30d = User.objects.filter(date_joined__gte=start_date).count()
    active_users = User.objects.filter(last_login__gte=start_date).count()

    # Chat stats
    total_sessions = ChatSession.objects.count()
    total_messages = ChatMessage.objects.count()
    sessions_30d = ChatSession.objects.filter(created_at__gte=start_date).count()

    # Daily stats for chart
    daily_stats = []
    for i in range(30):
        date = end_date - timedelta(days=29-i)
        users = User.objects.filter(date_joined__date=date).count()
        sessions = ChatSession.objects.filter(created_at__date=date).count()
        daily_stats.append({
            'date': date.strftime('%b %d'),
            'users': users,
            'sessions': sessions,
        })

    return render(request, 'wowdash/features/analytics_dashboard.html', {
        'total_users': total_users,
        'new_users_30d': new_users_30d,
        'active_users': active_users,
        'total_sessions': total_sessions,
        'total_messages': total_messages,
        'sessions_30d': sessions_30d,
        'daily_stats': json.dumps(daily_stats),
    })


# ============================================
# EMAIL NEWSLETTER
# ============================================

@login_required
@admin_required
def newsletter_manager(request):
    """Display newsletter manager"""
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)[:100]
    campaigns = NewsletterCampaign.objects.all()[:20]

    stats = {
        'total_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        'total_campaigns': NewsletterCampaign.objects.count(),
        'sent_campaigns': NewsletterCampaign.objects.filter(status='sent').count(),
    }

    return render(request, 'wowdash/features/newsletter_manager.html', {
        'subscribers': subscribers,
        'campaigns': campaigns,
        'stats': stats,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def newsletter_campaign_create(request):
    """Create newsletter campaign"""
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    campaign = NewsletterCampaign.objects.create(
        subject=data.get('subject'),
        content=data.get('content'),
        html_content=data.get('html_content', ''),
        status='draft',
        created_by=request.user,
    )

    return JsonResponse({'success': True, 'id': campaign.id})


@login_required
@admin_required
@require_http_methods(["POST"])
def newsletter_subscriber_add(request):
    """Add subscriber"""
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST

    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=data.get('email'),
        defaults={'name': data.get('name', '')}
    )

    return JsonResponse({'success': True, 'id': subscriber.id, 'created': created})


# ============================================
# PERSONAL AI ASSISTANT (CLAUDE OPUS 4.5)
# ============================================

@login_required
@admin_required
def ai_assistant(request):
    """Display AI Assistant chat interface"""
    conversations = AssistantConversation.objects.filter(user=request.user)[:20]

    # Get or create current conversation
    conversation_id = request.GET.get('conversation')
    if conversation_id:
        current_conversation = get_object_or_404(
            AssistantConversation, id=conversation_id, user=request.user
        )
    else:
        current_conversation = conversations.first()

    messages = []
    if current_conversation:
        messages = current_conversation.messages.all()

    return render(request, 'wowdash/features/ai_assistant.html', {
        'conversations': conversations,
        'current_conversation': current_conversation,
        'messages': messages,
    })


@login_required
@admin_required
@require_http_methods(["POST"])
def ai_assistant_chat(request):
    """Handle AI Assistant chat with Claude Opus 4.5"""
    import anthropic

    data = json.loads(request.body)
    message = data.get('message')
    conversation_id = data.get('conversation_id')

    # Get or create conversation
    if conversation_id:
        conversation = get_object_or_404(
            AssistantConversation, id=conversation_id, user=request.user
        )
    else:
        conversation = AssistantConversation.objects.create(
            user=request.user,
            title=message[:50] + '...' if len(message) > 50 else message
        )

    # Save user message
    AssistantMessage.objects.create(
        conversation=conversation,
        role='user',
        content=message
    )

    # Get conversation history
    history = []
    for msg in conversation.messages.all().order_by('timestamp')[:20]:
        history.append({
            'role': msg.role,
            'content': msg.content
        })

    # Call Claude Opus 4.5
    try:
        client = anthropic.Anthropic(
            api_key=os.environ.get('ANTHROPIC_API_KEY', '')
        )

        system_prompt = """You are a Personal AI Assistant for MarketingTool.Pro, powered by Claude Opus 4.5.

You help the admin with:
- Content creation (blogs, social media posts, ad copy)
- Marketing strategy and insights
- SEO recommendations
- Analyzing marketing trends
- Writing email newsletters
- Social media scheduling suggestions
- Website improvement ideas
- Business growth strategies

Be helpful, professional, and provide actionable advice. You have expertise in digital marketing, content creation, and business growth.

When creating content:
- Be creative and engaging
- Use persuasive copywriting techniques
- Optimize for the target platform
- Include relevant keywords naturally

Current date: """ + datetime.now().strftime('%Y-%m-%d')

        response = client.messages.create(
            model="claude-opus-4-5-20251101",
            max_tokens=4096,
            system=system_prompt,
            messages=history
        )

        assistant_message = response.content[0].text

        # Save assistant response
        AssistantMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_message
        )

        # Update conversation title if it's new
        if conversation.messages.count() == 2:
            conversation.title = message[:50] + '...' if len(message) > 50 else message
            conversation.save()

        return JsonResponse({
            'success': True,
            'message': assistant_message,
            'conversation_id': conversation.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@admin_required
@require_http_methods(["POST"])
def ai_assistant_new_conversation(request):
    """Create new conversation"""
    conversation = AssistantConversation.objects.create(
        user=request.user,
        title='New Conversation'
    )
    return JsonResponse({'success': True, 'id': conversation.id})


@login_required
@admin_required
@require_http_methods(["DELETE"])
def ai_assistant_delete_conversation(request, conversation_id):
    """Delete conversation"""
    conversation = get_object_or_404(
        AssistantConversation, id=conversation_id, user=request.user
    )
    conversation.delete()
    return JsonResponse({'success': True})
