from wowdash_app.utils import log_error_to_file
from Dal.wowdash_app.dashboard import (
    get_recent_users, get_top_performers, get_user_statistics, get_subscription_trends,
    get_user_trends, get_generated_content_stats,
    get_blog_statistics, get_team_data, get_release_data, get_chat_statistics,
    get_support_statistics, get_session_statistics, get_user_activity, get_30_day_statistics,
    get_user_profile_by_id, update_user_profile_status, get_subscriber_data,
    get_user_overview_data, get_generated_content_data
)

def get_dashboard_data():
    """Get all dashboard data"""
    try:
        # Get all data from DAL
        users = get_recent_users()
        top_performers = get_top_performers()
        user_stats = get_user_statistics()
        subscription_trends = get_subscription_trends()
        user_trends = get_user_trends()
        generated_content_stats = get_generated_content_stats()
        blog_stats = get_blog_statistics()
        team_data = get_team_data()
        release_data = get_release_data()
        chat_stats = get_chat_statistics()
        support_stats = get_support_statistics()
        session_stats = get_session_statistics()
        user_activity = get_user_activity()
        stats_30_day = get_30_day_statistics()
        user_overview = get_user_overview_data('today')
        
        # Combine all data
        return {
            'users': users,
            'top_performers': top_performers,
            
            # User Stats
            'total_users': user_stats['total_users'],
            'total_free_users': user_stats['total_free_users'],
            'total_subscriptions': user_stats['total_subscriptions'],
            'subscription_trend': subscription_trends['subscription_trend'],
            'subscription_trend_abs': subscription_trends['subscription_trend_abs'],
            'subscription_trend_percent': subscription_trends['subscription_trend_percent'],
            'active_users_24h': user_trends['active_users_24h'],
            'user_trend': user_trends['user_trend'],
            'user_trend_abs': user_trends['user_trend_abs'],
            
            # Generated Content Stats
            'total_words': generated_content_stats['total_words'],
            'total_images': generated_content_stats['total_images'],
            
            # Blog Stats
            'total_posts': blog_stats['total_posts'],
            'recent_posts': blog_stats['recent_posts'],
            'total_blog_views': blog_stats['total_blog_views'],
            'blog_trend': blog_stats['blog_trend'],
            'blog_trend_abs': blog_stats['blog_trend_abs'],
            
            # Team Stats
            'featured_team': team_data['featured_team'],
            'total_team_members': team_data['total_team_members'],
            
            # Release Stats
            'latest_release': release_data['latest_release'],
            'total_releases': release_data['total_releases'],
            
            # Chat Stats
            'total_chat_sessions': chat_stats['total_chat_sessions'],
            'total_chat_messages': chat_stats['total_chat_messages'],
            'recent_chat_sessions': chat_stats['recent_chat_sessions'],
            'chat_trend': chat_stats['chat_trend'],
            'chat_trend_abs': chat_stats['chat_trend_abs'],
            
            # Support Stats
            'total_queries': support_stats['total_queries'],
            'unread_queries': support_stats['unread_queries'],
            'total_faqs': support_stats['total_faqs'],
            'query_trend': support_stats['query_trend'],
            'query_trend_abs': support_stats['query_trend_abs'],
            
            # Session Stats
            'active_sessions': session_stats['active_sessions'],
            'session_trend': session_stats['session_trend'],
            'session_trend_abs': session_stats['session_trend_abs'],
            'user_activity': user_activity,
            
            # 30-day Stats
            'users_30': stats_30_day['users_30'],
            'subscriptions_30': stats_30_day['subscriptions_30'],
            'free_users_30': stats_30_day['free_users_30'],
            
            # Card-specific trends
            'users_trend': user_trends['users_trend'],
            'users_trend_abs': user_trends['users_trend_abs'],
            'free_users_trend': user_trends['free_users_trend'],
            'free_users_trend_abs': user_trends['free_users_trend_abs'],
            'total_sessions': chat_stats['total_chat_sessions'],
            'total_messages': chat_stats['total_chat_messages'],
            'message_trend': chat_stats['message_trend'],
            'message_trend_abs': chat_stats['message_trend_abs'],
            # Add new_users and subscribed_users for dashboard cards
            'new_users': user_overview['new_users'],
            'subscribed_users': user_overview['subscribed_users'],
        }
    except Exception as e:
        log_error_to_file(e)

def toggle_user_status_business(user_id):
    """Business logic for toggling user status"""
    try:
        user_profile = get_user_profile_by_id(user_id)
        
        # Business rule: Prevent deactivating superusers
        if user_profile.user.is_superuser:
            raise ValueError('Cannot deactivate superuser.')
        
        # Toggle status
        new_status = not user_profile.is_active
        updated_profile = update_user_profile_status(user_profile, new_status)
        
        return {
            'success': True,
            'status': 'Active' if updated_profile.is_active else 'Inactive',
            'status_message': f"User {'activated' if updated_profile.is_active else 'deactivated'} successfully."
        }
    except Exception as e:
        log_error_to_file(e)

def get_statistics_data(stat_type, period):
    """Get statistics data based on type and period"""
    try:
        # Map period values to match the frontend
        period_map = {
            'today': 'today',
            'weekly': 'week',
            'monthly': 'month',
            'yearly': 'year'
        }
        period = period_map.get(period, period)
        
        if stat_type == 'subscriber':
            return get_subscriber_data(period)
        elif stat_type == 'user_overview':
            return get_user_overview_data(period)
        elif stat_type == 'generated_content':
            return get_generated_content_data(period)
        else:
            raise ValueError('Invalid stat type')
    except Exception as e:
        log_error_to_file(e)
