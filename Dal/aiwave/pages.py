from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Count
from django.core.paginator import Paginator
from django.utils.text import slugify
from wowdash_app.utils import log_error_to_file
from django.contrib.sessions.models import Session
from wowdash_app.models import (
    ContentSetting, FAQ, UserQueries, TeamMember, Blog, 
    ReleaseNote, ChatSession, ChatMessage, UserSession
)

def get_team_members_dal():
    """Get all team members ordered by featured status and order"""
    try:
        return TeamMember.objects.all().order_by('-featured', 'order', 'name')
    except Exception as e:
        log_error_to_file(e)

def get_content_setting_dal(key):
    """Get content setting by key"""
    try:
        return ContentSetting.objects.filter(key=key).first()
    except Exception as e:
        log_error_to_file(e)

def get_published_blogs_dal():
    """Get all published blog posts"""
    try:
        return Blog.objects.filter(is_published=True)
    except Exception as e:
        log_error_to_file(e)

def search_blogs_dal(posts, search_query):
    """Search blogs by query"""
    try:
        if search_query:
            return posts.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(category__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            ).distinct()
        return posts
    except Exception as e:
        log_error_to_file(e)

def filter_blogs_by_category_dal(posts, category):
    """Filter blogs by category"""
    try:
        if category:
            return posts.filter(category=category)
        return posts
    except Exception as e:
        log_error_to_file(e)

def get_blog_categories_dal():
    """Get categories with post counts"""
    try:
        return Blog.objects.filter(is_published=True).values('category').annotate(
            count=Count('id')
        ).order_by('category')
    except Exception as e:
        log_error_to_file(e)

def get_blog_tags_dal():
    """Get all unique tags from published blogs"""
    try:
        all_tags = set()
        for post in Blog.objects.filter(is_published=True):
            if post.tags:
                all_tags.update(tag.strip() for tag in post.tags.split())
        return sorted(all_tags)
    except Exception as e:
        log_error_to_file(e)

def paginate_blogs_dal(posts, page_number, per_page=8):
    """Paginate blog posts"""
    try:
        paginator = Paginator(posts.order_by('-created_at'), per_page)
        return paginator.get_page(page_number)
    except Exception as e:
        log_error_to_file(e)

def get_blog_by_slug_dal(slug):
    """Get blog post by slug"""
    try:
        return get_object_or_404(Blog, slug=slug, is_published=True)
    except Exception as e:
        log_error_to_file(e)

def increment_blog_views_dal(blog_id):
    """Increment blog view count"""
    try:
        Blog.objects.filter(id=blog_id).update(views=F('views') + 1)
    except Exception as e:
        log_error_to_file(e)

def get_related_blogs_dal(category, exclude_id):
    """Get related blog posts by category"""
    try:
        return Blog.objects.filter(
            category=category,
            is_published=True
        ).exclude(id=exclude_id)[:3]
    except Exception as e:
        log_error_to_file(e)

def get_recent_blogs_dal(exclude_id=None):
    """Get recent blog posts"""
    try:
        qs = Blog.objects.filter(is_published=True)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.order_by('-created_at')[:3]
    except Exception as e:
        log_error_to_file(e)

def get_blog_archives_dal():
    """Get blog post archives grouped by month"""
    try:
        from django.db.models.functions import TruncMonth
        return Blog.objects.filter(
            is_published=True
        ).annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('-month')[:7]
    except Exception as e:
        log_error_to_file(e)

def create_blog_post_dal(title, content, excerpt, category, tags, featured_image, author):
    """Create a new blog post"""
    try:
        slug = slugify(title)
        return Blog.objects.create(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            category=category,
            tags=tags,
            featured_image=featured_image,
            author=author,
            is_published=True
        )
    except Exception as e:
        log_error_to_file(e)

def get_user_chat_sessions_dal(user):
    """Get all chat sessions for a user"""
    try:
        return ChatSession.objects.filter(user=user)
    except Exception as e:
        log_error_to_file(e)

def get_chat_session_messages_dal(session):
    """Get messages for a chat session"""
    try:
        return ChatMessage.objects.filter(session=session).order_by('timestamp')
    except Exception as e:
        log_error_to_file(e)

def get_user_sessions_dal(user):
    """Get active user sessions"""
    try:
        return UserSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-last_activity')
    except Exception as e:
        log_error_to_file(e)

def get_user_session_by_id_dal(session_id, user):
    """Get specific user session by ID"""
    try:
        return UserSession.objects.get(id=session_id, user=user)
    except UserSession.DoesNotExist:
        raise UserSession.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def delete_django_session_dal(session_key):
    """Delete session from Django's session store"""
    try:
        Session.objects.filter(session_key=session_key).delete()
    except Exception as e:
        log_error_to_file(e)

def update_user_session_status_dal(session, is_active):
    """Update user session active status"""
    try:
        session.is_active = is_active
        session.save()
        return session
    except Exception as e:
        log_error_to_file(e)

def get_other_user_sessions_dal(user, current_session_key):
    """Get all user sessions except current"""
    try:
        return UserSession.objects.filter(
            user=user,
            is_active=True
        ).exclude(session_key=current_session_key)
    except Exception as e:
        log_error_to_file(e)

def create_or_update_user_session_dal(session_key, user, ip_address, user_agent, device_info, browser_info):
    """Create or update user session record"""
    try:
        return UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user': user,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'device_info': device_info,
                'browser_info': browser_info,
                'is_active': True
            }
        )
    except Exception as e:
        log_error_to_file(e)

def get_release_notes_dal():
    """Get all release notes ordered by date and version"""
    try:
        return ReleaseNote.objects.all().order_by('-release_date', '-version')
    except Exception as e:
        log_error_to_file(e)

def get_faq_categories_dal():
    """Get FAQ categories"""
    try:
        return FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    except Exception as e:
        log_error_to_file(e)

def get_faqs_by_category_dal():
    """Get FAQs grouped by category"""
    try:
        faqs = FAQ.objects.filter(is_active=True)
        faqs_by_category = {}
        for faq in faqs:
            if faq.category not in faqs_by_category:
                faqs_by_category[faq.category] = []
            faqs_by_category[faq.category].append(faq)
        return faqs_by_category
    except Exception as e:
        log_error_to_file(e)

def create_user_query_dal(name, email, subject, phone, message):
    """Create a new user query"""
    try:
        return UserQueries.objects.create(
            name=name,
            email=email,
            subject=subject,
            phone=phone,
            message=message
        )
    except Exception as e:
        log_error_to_file(e)

def update_user_profile_dal(user, full_name, email, username=None):
    """Update user profile information"""
    try:
        if full_name:
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            if len(names) > 1:
                user.last_name = names[1]
        if email:
            user.email = email
        if username:
            user.username = username
        user.save()
        return user
    except Exception as e:
        log_error_to_file(e)

def update_user_profile_picture_dal(profile, profile_picture):
    """Update user profile picture"""
    try:
        profile.profile_picture = profile_picture
        profile.save()
        return profile
    except Exception as e:
        log_error_to_file(e)

def delete_blog_post_dal(blog_id, user):
    """Delete a blog post if the user is the author"""
    try:
        blog = Blog.objects.get(id=blog_id, author=user)
        blog.delete()
        return True
    except Blog.DoesNotExist:
        return False
    except Exception as e:
        log_error_to_file(e)
        return False
