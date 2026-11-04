from Dal.aiwave.pages import (
    get_team_members_dal,
    get_content_setting_dal,
    get_published_blogs_dal,
    search_blogs_dal,
    filter_blogs_by_category_dal,
    get_blog_categories_dal,
    get_blog_tags_dal,
    paginate_blogs_dal,
    get_blog_by_slug_dal,
    increment_blog_views_dal,
    get_related_blogs_dal,
    get_recent_blogs_dal,
    get_blog_archives_dal,
    create_blog_post_dal,
    get_user_chat_sessions_dal,
    get_chat_session_messages_dal,
    get_user_sessions_dal,
    get_user_session_by_id_dal,
    delete_django_session_dal,
    update_user_session_status_dal,
    get_other_user_sessions_dal,
    create_or_update_user_session_dal,
    get_release_notes_dal,
    get_faq_categories_dal,
    get_faqs_by_category_dal,
    create_user_query_dal,
    update_user_profile_dal,
    update_user_profile_picture_dal,
)
from user_agents import parse
from wowdash_app.utils import log_error_to_file

def get_team_data_bal():
    """Get team members data"""
    try:
        team_members = get_team_members_dal()
        return team_members
    except Exception as e:
        log_error_to_file(e)

def get_content_data_bal(key):
    """Get content setting data"""
    try:
        content_setting = get_content_setting_dal(key)
        return content_setting.value if content_setting else None
    except Exception as e:
        log_error_to_file(e)

def get_blog_list_data_bal(search_query, category, page_number):
    """Get blog list data with search and filtering"""
    try:
        # Get all published blogs
        posts = get_published_blogs_dal()
        
        # Get total count before filtering
        total_posts_count = posts.count()
        
        # Apply search filter
        posts = search_blogs_dal(posts, search_query)
        
        # Apply category filter
        posts = filter_blogs_by_category_dal(posts, category)
        
        # Get categories and tags
        categories = get_blog_categories_dal()
        all_tags = get_blog_tags_dal()
        
        # Paginate results
        paginated_posts = paginate_blogs_dal(posts, page_number)

        # Get recent posts for sidebar
        recent_posts = get_recent_blogs_dal()

        # Get archives for sidebar
        archives = get_blog_archives_dal()

        return {
            'posts': paginated_posts,
            'categories': categories,
            'all_tags': all_tags,
            'recent_posts': recent_posts,
            'archives': archives,
            'search_query': search_query,
            'selected_category': category,
            'total_posts_count': total_posts_count
        }
    except Exception as e:
        log_error_to_file(e)

def get_blog_detail_data_bal(slug):
    """Get blog detail data with related posts"""
    try:
        # Get the blog post
        post = get_blog_by_slug_dal(slug)
        
        # Increment view count
        increment_blog_views_dal(post.id)
        post.refresh_from_db()
        
        # Get related and recent posts
        related_posts = get_related_blogs_dal(post.category, post.id)
        recent_posts = get_recent_blogs_dal(post.id)
        
        # Get categories
        categories = get_blog_categories_dal()

        # Get archives
        archives = get_blog_archives_dal()

        # Get total posts count
        total_posts_count = get_published_blogs_dal().count()

        return {
            'post': post,
            'related_posts': related_posts,
            'recent_posts': recent_posts,
            'categories': categories,
            'archives': archives,
            'total_posts_count': total_posts_count
        }
    except Exception as e:
        log_error_to_file(e)

def create_blog_post_bal(title, content, excerpt, category, tags, featured_image, author):
    """Create a new blog post"""
    try:
        blog = create_blog_post_dal(title, content, excerpt, category, tags, featured_image, author)
        return blog
    except Exception as e:
        log_error_to_file(e)

def get_chat_export_data_bal(user):
    """Get chat export data grouped by bot mode"""
    try:
        chat_sessions = get_user_chat_sessions_dal(user)
        
        # Group sessions by bot mode
        bot_modes = {}
        for session in chat_sessions:
            if session.bot_mode not in bot_modes:
                bot_modes[session.bot_mode] = {
                    'count': 0,
                    'sessions': []
                }
            bot_modes[session.bot_mode]['count'] += 1
            bot_modes[session.bot_mode]['sessions'].append({
                'id': session.session_id,
                'title': session.title,
                'created_at': session.created_at,
                'modified_at': session.modified_at
            })
        
        return bot_modes
    except Exception as e:
        log_error_to_file(e)

def export_chat_sessions_bal(session_ids, user):
    """Export selected chat sessions"""
    try:
        from Dal.aiwave.pages import ChatSession, ChatMessage
        
        # Get the selected sessions
        sessions = ChatSession.objects.filter(
            session_id__in=session_ids,
            user=user
        )

        # Prepare the export data
        export_data = []
        for session in sessions:
            messages = get_chat_session_messages_dal(session)
            
            session_data = {
                'title': session.title,
                'bot_mode': session.bot_mode,
                'created_at': session.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'messages': []
            }
            
            for message in messages:
                session_data['messages'].append({
                    'is_bot': message.is_bot_response,
                    'content': message.message,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            
            export_data.append(session_data)

        return export_data
    except Exception as e:
        log_error_to_file(e)

def get_active_sessions_data_bal(user, current_session_key):
    """Get active sessions data for user"""
    try:
        sessions = get_user_sessions_dal(user)
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'device_info': session.device_info,
                'browser_info': session.browser_info,
                'ip_address': session.ip_address,
                'last_activity': session.last_activity.strftime('%Y-%m-%d %H:%M:%S'),
                'is_current': session.session_key == current_session_key
            })
        
        return sessions_data
    except Exception as e:
        log_error_to_file(e)

def terminate_user_session_bal(session_id, user, current_session_key):
    """Terminate a specific user session"""
    try:
        session = get_user_session_by_id_dal(session_id, user)
        
        # Don't allow terminating current session
        if session.session_key == current_session_key:
            raise ValueError("Cannot terminate current session")
        
        # Delete from Django's session store
        delete_django_session_dal(session.session_key)
        
        # Mark as inactive in our database
        update_user_session_status_dal(session, False)
        
        return True
    except Exception as e:
        log_error_to_file(e)

def terminate_all_other_sessions_bal(user, current_session_key):
    """Terminate all sessions except the current one"""
    try:
        sessions = get_other_user_sessions_dal(user, current_session_key)

        for session in sessions:
            # Delete from Django's session store
            delete_django_session_dal(session.session_key)
            # Mark as inactive in our database
            update_user_session_status_dal(session, False)

        return True
    except Exception as e:
        log_error_to_file(e)

def create_session_record_bal(request, user):
    """Create a new session record when user logs in"""
    try:
        user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
        device_info = f"{user_agent.device.family} {user_agent.os.family} {user_agent.os.version_string}"
        browser_info = f"{user_agent.browser.family} {user_agent.browser.version_string}"

        # Create or update session record
        create_or_update_user_session_dal(
            request.session.session_key,
            user,
            request.META.get('REMOTE_ADDR'),
            request.META.get('HTTP_USER_AGENT', ''),
            device_info,
            browser_info
        )
    except Exception as e:
        log_error_to_file(e)

def get_release_notes_data_bal():
    """Get release notes data"""
    try:
        return get_release_notes_dal()
    except Exception as e:
        log_error_to_file(e)

def get_help_faq_data_bal():
    """Get help and FAQ data"""
    try:
        faq_categories = get_faq_categories_dal()
        faqs_by_category = get_faqs_by_category_dal()
        
        return {
            'faq_categories': faq_categories,
            'faqs_by_category': faqs_by_category
        }
    except Exception as e:
        log_error_to_file(e)

def process_help_contact_bal(name, email, subject, phone, message):
    """Process help contact form submission"""
    try:
        # Validate required fields
        if not all([name, email, subject, phone, message]):
            raise ValueError("Please fill in all fields.")
        
        # Create user query
        contact_message = create_user_query_dal(name, email, subject, phone, message)
        return contact_message
    except Exception as e:
        log_error_to_file(e)

def update_user_profile_bal(user, full_name, email, profile_picture, username=None):
    """Update user profile information"""
    try:
        # Update user fields
        if full_name or email or username:
            update_user_profile_dal(user, full_name, email, username)
        
        # Update profile picture
        if profile_picture:
            update_user_profile_picture_dal(user.profile, profile_picture)
        
        return True
    except Exception as e:
        log_error_to_file(e)

def delete_blog_post_bal(blog_id, user):
    """Delete a blog post via DAL"""
    from Dal.aiwave.pages import delete_blog_post_dal
    return delete_blog_post_dal(blog_id, user)