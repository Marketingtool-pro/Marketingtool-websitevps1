from django.db import models
from django.db.models import Count, Max
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from decimal import Decimal
from wowdash_app.utils import log_error_to_file
from wowdash_app.models import UserActivity, Blog, TeamMember, ReleaseNote, UserSession, UserQueries, FAQ, ChatSession, ChatMessage, UserProfile, Subscription, GeneratedContent

def normalize_decimal(value):
    """Remove trailing zeros from decimal values"""
    if isinstance(value, Decimal):
        return value.normalize()
    elif isinstance(value, float):
        return Decimal(str(value)).normalize()
    return value

def get_time_period_data(model, amount_field, time_period):
    """Get data for different time periods"""
    now = timezone.now()
    
    if time_period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        interval = 'hour'
        format_str = '%H:00'
    elif time_period == 'week':
        start_date = now - timedelta(days=7)
        interval = 'day'
        format_str = '%a'
    elif time_period == 'month':
        start_date = now - timedelta(days=30)
        interval = 'day'
        format_str = '%d %b'
    elif time_period == 'year':
        start_date = now - timedelta(days=365)
        interval = 'month'
        format_str = '%b %Y'
    else:
        start_date = now - timedelta(days=30)
        interval = 'day'
        format_str = '%d %b'
    
    # Generate time labels
    labels = []
    current = start_date
    while current <= now:
        labels.append(current.strftime(format_str))
        if interval == 'hour':
            current += timedelta(hours=1)
        elif interval == 'day':
            current += timedelta(days=1)
        else:  # month
            current += timedelta(days=30)
    
    # Prepare data series
    data_points = [0] * len(labels)
    
    # Get data for each time point
    for i, label in enumerate(labels):
        if interval == 'hour':
            start = start_date + timedelta(hours=i)
            end = start + timedelta(hours=1)
        elif interval == 'day':
            start = start_date + timedelta(days=i)
            end = start + timedelta(days=1)
        else:  # month
            start = start_date + timedelta(days=i*30)
            end = start + timedelta(days=30)
        
        if amount_field:
            value = model.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            ).aggregate(total=models.Sum(amount_field))['total'] or 0
            data_points[i] = normalize_decimal(value)
        else:
            data_points[i] = model.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            ).count()
    
    return {
        'data': data_points,
        'labels': labels,
        'total': sum(data_points),
        'start_date': start_date
    }

def get_recent_users(limit=20):
    """Get the latest 20 registered users with their profiles (regardless of session)"""
    try:
        return User.objects.select_related('profile').all().order_by('-date_joined')[:limit]
    except Exception as e:
        log_error_to_file(e)

def get_top_performers(limit=8):
    """Get top performers based on activity and usage"""
    try:
        return User.objects.select_related('profile').annotate(
            total_chat_sessions=Count('chat_sessions'),
            total_generated_content=Count('generatedcontent'),
            last_activity=Max('activity__last_login_time')
        ).order_by('-total_chat_sessions', '-total_generated_content')[:limit]
    except Exception as e:
        log_error_to_file(e)

def get_user_statistics():
    """Get user statistics"""
    try:
        total_users = User.objects.count()
        total_free_users = UserProfile.objects.filter(role='user').count()
        total_subscriptions = Subscription.objects.filter(is_active=True).count()
        
        return {
            'total_users': total_users,
            'total_free_users': total_free_users,
            'total_subscriptions': total_subscriptions
        }
    except Exception as e:
        log_error_to_file(e)

def get_subscription_trends():
    """Get subscription trends"""
    try:
        now = timezone.now()
        subscriptions_24h = Subscription.objects.filter(
            created_at__gte=now - timedelta(hours=24),
            is_active=True
        ).count()
        subscriptions_48h = Subscription.objects.filter(
            created_at__gte=now - timedelta(hours=48),
            created_at__lt=now - timedelta(hours=24),
            is_active=True
        ).count()
        
        subscription_trend = subscriptions_24h - subscriptions_48h
        subscription_trend_abs = abs(subscription_trend)
        
        if subscriptions_48h > 0:
            subscription_trend_percent = (subscription_trend / subscriptions_48h) * 100
        else:
            subscription_trend_percent = 0 if subscription_trend == 0 else 100
            
        return {
            'subscription_trend': subscription_trend,
            'subscription_trend_abs': subscription_trend_abs,
            'subscription_trend_percent': subscription_trend_percent
        }
    except Exception as e:
        log_error_to_file(e)


def get_user_trends():
    """Get user trends"""
    try:
        now = timezone.now()
        
        # Free users trend
        free_users_24h = UserProfile.objects.filter(
            role='user',
            user__date_joined__gte=now - timedelta(hours=24)
        ).count()
        free_users_48h = UserProfile.objects.filter(
            role='user',
            user__date_joined__gte=now - timedelta(hours=48),
            user__date_joined__lt=now - timedelta(hours=24)
        ).count()
        free_users_trend = free_users_24h - free_users_48h
        free_users_trend_abs = abs(free_users_trend)

        # Users trend
        users_24h = User.objects.filter(
            date_joined__gte=now - timedelta(hours=24)
        ).count()
        users_48h = User.objects.filter(
            date_joined__gte=now - timedelta(hours=48),
            date_joined__lt=now - timedelta(hours=24)
        ).count()
        users_trend = users_24h - users_48h
        users_trend_abs = abs(users_trend)
        
        # Active users
        active_users_24h = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=timezone.now() - timedelta(hours=24)
        ).values('user').distinct().count()
        
        users_48h_ago = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=timezone.now() - timedelta(hours=48),
            last_activity__lt=timezone.now() - timedelta(hours=24)
        ).values('user').distinct().count()
        user_trend = active_users_24h - users_48h_ago
        user_trend_abs = abs(user_trend)
        
        return {
            'free_users_trend': free_users_trend,
            'free_users_trend_abs': free_users_trend_abs,
            'users_trend': users_trend,
            'users_trend_abs': users_trend_abs,
            'active_users_24h': active_users_24h,
            'user_trend': user_trend,
            'user_trend_abs': user_trend_abs
        }
    except Exception as e:
        log_error_to_file(e)

def get_generated_content_stats():
    """Get generated content statistics"""
    try:
        total_words = GeneratedContent.objects.filter(content_type='word').count()
        total_images = GeneratedContent.objects.filter(content_type='image').count()
        
        return {
            'total_words': total_words,
            'total_images': total_images
        }
    except Exception as e:
        log_error_to_file(e)

def get_blog_statistics():
    """Get blog statistics"""
    try:
        total_posts = Blog.objects.count()
        recent_posts = Blog.objects.filter(is_published=True).order_by('-created_at')[:5]
        total_blog_views = Blog.objects.aggregate(total_views=Count('views'))['total_views']
        
        # Blog views trend
        now = timezone.now()
        blog_views_24h = Blog.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).aggregate(views=Count('views'))['views'] or 0
        blog_views_48h = Blog.objects.filter(
            created_at__gte=now - timedelta(hours=48),
            created_at__lt=now - timedelta(hours=24)
        ).aggregate(views=Count('views'))['views'] or 0
        blog_trend = blog_views_24h - blog_views_48h
        blog_trend_abs = abs(blog_trend)
        
        return {
            'total_posts': total_posts,
            'recent_posts': recent_posts,
            'total_blog_views': total_blog_views,
            'blog_trend': blog_trend,
            'blog_trend_abs': blog_trend_abs
        }
    except Exception as e:
        log_error_to_file(e)

def get_team_data():
    """Get team data"""
    try:
        featured_team = TeamMember.objects.filter(featured=True).order_by('order')[:3]
        total_team_members = TeamMember.objects.count()
        
        return {
            'featured_team': featured_team,
            'total_team_members': total_team_members
        }
    except Exception as e:
        log_error_to_file(e)

def get_release_data():
    """Get release data"""
    try:
        latest_release = ReleaseNote.objects.order_by('-release_date').first()
        total_releases = ReleaseNote.objects.count()
        
        return {
            'latest_release': latest_release,
            'total_releases': total_releases
        }
    except Exception as e:
        log_error_to_file(e)

def get_chat_statistics():
    """Get chat statistics"""
    try:
        total_chat_sessions = ChatSession.objects.count()
        total_chat_messages = ChatMessage.objects.count()
        recent_chat_sessions = ChatSession.objects.select_related('user').order_by('-modified_at')[:5]

        # Chat trend
        now = timezone.now()
        chat_sessions_24h = ChatSession.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        chat_sessions_48h = ChatSession.objects.filter(
            created_at__gte=now - timedelta(hours=48),
            created_at__lt=now - timedelta(hours=24)
        ).count()
        chat_trend = chat_sessions_24h - chat_sessions_48h
        chat_trend_abs = abs(chat_trend)

        # Message trend
        messages_24h = ChatMessage.objects.filter(
            timestamp__gte=now - timedelta(hours=24)
        ).count()
        messages_48h = ChatMessage.objects.filter(
            timestamp__gte=now - timedelta(hours=48),
            timestamp__lt=now - timedelta(hours=24)
        ).count()
        message_trend = messages_24h - messages_48h
        message_trend_abs = abs(message_trend)
        
        return {
            'total_chat_sessions': total_chat_sessions,
            'total_chat_messages': total_chat_messages,
            'recent_chat_sessions': recent_chat_sessions,
            'chat_trend': chat_trend,
            'chat_trend_abs': chat_trend_abs,
            'message_trend': message_trend,
            'message_trend_abs': message_trend_abs
        }
    except Exception as e:
        log_error_to_file(e)

def get_support_statistics():
    """Get support statistics"""
    try:
        total_queries = UserQueries.objects.count()
        unread_queries = UserQueries.objects.filter(is_read=False).count()
        total_faqs = FAQ.objects.filter(is_active=True).count()
        
        # Query trend
        now = timezone.now()
        queries_24h = UserQueries.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        queries_48h = UserQueries.objects.filter(
            created_at__gte=now - timedelta(hours=48),
            created_at__lt=now - timedelta(hours=24)
        ).count()
        query_trend = queries_24h - queries_48h
        query_trend_abs = abs(query_trend)
        
        return {
            'total_queries': total_queries,
            'unread_queries': unread_queries,
            'total_faqs': total_faqs,
            'query_trend': query_trend,
            'query_trend_abs': query_trend_abs
        }
    except Exception as e:
        log_error_to_file(e)

def get_session_statistics():
    """Get session statistics"""
    try:
        active_sessions = UserSession.objects.filter(
            is_active=True,
            last_activity__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Session trend
        now = timezone.now()
        sessions_24h = UserSession.objects.filter(
            created_at__gte=now - timedelta(hours=24)
        ).count()
        sessions_48h = UserSession.objects.filter(
            created_at__gte=now - timedelta(hours=48),
            created_at__lt=now - timedelta(hours=24)
        ).count()
        session_trend = sessions_24h - sessions_48h
        session_trend_abs = abs(session_trend)
        
        return {
            'active_sessions': active_sessions,
            'session_trend': session_trend,
            'session_trend_abs': session_trend_abs
        }
    except Exception as e:
        log_error_to_file(e)

def get_user_activity():
    """Get user activity"""
    try:
        return UserActivity.objects.select_related('user').order_by('-last_login_time')[:5]
    except Exception as e:
        log_error_to_file(e)

def get_30_day_statistics():
    """Get 30-day statistics"""
    try:
        now = timezone.now()
        last_30 = now - timedelta(days=30)
        users_30 = User.objects.filter(date_joined__gte=last_30).count()
        subscriptions_30 = Subscription.objects.filter(created_at__gte=last_30, is_active=True).count()
        free_users_30 = UserProfile.objects.filter(user__date_joined__gte=last_30, role='user').count()
        
        return {
            'users_30': users_30,
            'subscriptions_30': subscriptions_30,
            'free_users_30': free_users_30
        }
    except Exception as e:
        log_error_to_file(e)

def get_user_profile_by_id(user_id):
    """Get user profile by ID"""
    try:
        return UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        raise UserProfile.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def update_user_profile_status(user_profile, is_active):
    """Update user profile status"""
    try:
        user_profile.is_active = is_active
        user_profile.save()
        return user_profile
    except Exception as e:
        log_error_to_file(e)

def get_subscriber_data(period):
    """Get subscriber data for statistics"""
    try:
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            interval = 'hour'
            format_str = '%H:00'
        elif period == 'week':
            start_date = now - timedelta(days=7)
            interval = 'day'
            format_str = '%a'
        elif period == 'month':
            start_date = now - timedelta(days=30)
            interval = 'day'
            format_str = '%d %b'
        else:  # year
            start_date = now - timedelta(days=365)
            interval = 'month'
            format_str = '%b %Y'

        # Generate time labels
        labels = []
        current = start_date
        while current <= now:
            labels.append(current.strftime(format_str))
            if interval == 'hour':
                current += timedelta(hours=1)
            elif interval == 'day':
                current += timedelta(days=1)
            else:  # month
                current += timedelta(days=30)

        # Get subscriber data
        subscriber_data = []
        for i, label in enumerate(labels):
            if interval == 'hour':
                start = start_date + timedelta(hours=i)
                end = start + timedelta(hours=1)
            elif interval == 'day':
                start = start_date + timedelta(days=i)
                end = start + timedelta(days=1)
            else:  # month
                start = start_date + timedelta(days=i*30)
                end = start + timedelta(days=30)
            
            count = Subscription.objects.filter(
                created_at__gte=start,
                created_at__lt=end,
                is_active=True
            ).count()
            subscriber_data.append(count)

        return {
            'subscriber_data': subscriber_data,
            'labels': labels
        }
    except Exception as e:
        log_error_to_file(e)

def get_user_overview_data(period):
    """Get user overview data for statistics"""
    try:
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)

        active_users = UserSession.objects.filter(
            last_activity__gte=start_date,
            is_active=True
        ).values('user').distinct().count()

        new_users = User.objects.filter(
            date_joined__gte=start_date
        ).count()

        subscribed_users = Subscription.objects.filter(
            created_at__gte=start_date,
            is_active=True
        ).count()

        total_users = User.objects.count()

        return {
            'active_users': active_users,
            'new_users': new_users,
            'subscribed_users': subscribed_users,
            'total_users': total_users
        }
    except Exception as e:
        log_error_to_file(e)

def get_generated_content_data(period):
    """Get generated content data for statistics"""
    try:
        now = timezone.now()
        if period == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            interval = 'hour'
            format_str = '%H:00'
        elif period == 'week':
            start_date = now - timedelta(days=7)
            interval = 'day'
            format_str = '%a'
        elif period == 'month':
            start_date = now - timedelta(days=30)
            interval = 'day'
            format_str = '%d %b'
        else:  # year
            start_date = now - timedelta(days=365)
            interval = 'month'
            format_str = '%b %Y'

        # Generate time labels
        labels = []
        current = start_date
        while current <= now:
            labels.append(current.strftime(format_str))
            if interval == 'hour':
                current += timedelta(hours=1)
            elif interval == 'day':
                current += timedelta(days=1)
            else:  # month
                current += timedelta(days=30)

        # Get sessions data
        sessions_data = []
        total_sessions = 0
        for i, label in enumerate(labels):
            if interval == 'hour':
                start = start_date + timedelta(hours=i)
                end = start + timedelta(hours=1)
            elif interval == 'day':
                start = start_date + timedelta(days=i)
                end = start + timedelta(days=1)
            else:  # month
                start = start_date + timedelta(days=i*30)
                end = start + timedelta(days=30)
            
            count = ChatSession.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            ).count()
            sessions_data.append(count)
            total_sessions += count

        # Get messages data
        messages_data = []
        total_messages = 0
        for i, label in enumerate(labels):
            if interval == 'hour':
                start = start_date + timedelta(hours=i)
                end = start + timedelta(hours=1)
            elif interval == 'day':
                start = start_date + timedelta(days=i)
                end = start + timedelta(days=1)
            else:  # month
                start = start_date + timedelta(days=i*30)
                end = start + timedelta(days=30)
            
            count = ChatMessage.objects.filter(
                timestamp__gte=start,
                timestamp__lt=end
            ).count()
            messages_data.append(count)
            total_messages += count

        # Get today's totals
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_sessions = ChatSession.objects.filter(
            created_at__gte=today_start
        ).count()
        today_messages = ChatMessage.objects.filter(
            timestamp__gte=today_start
        ).count()

        return {
            'sessions_data': sessions_data,
            'messages_data': messages_data,
            'labels': labels,
            'total_sessions': today_sessions,
            'total_messages': today_messages,
            'period_total_sessions': total_sessions,
            'period_total_messages': total_messages
        }
    except Exception as e:
        log_error_to_file(e)
