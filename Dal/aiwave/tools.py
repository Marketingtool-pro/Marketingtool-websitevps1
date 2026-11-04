from django.utils.timezone import now
from wowdash_app.models import ChatMessage, ChatSession
from wowdash_app.utils import send_message_to_gemini
from wowdash_app.utils import log_error_to_file
import uuid

def create_or_get_chat_session_dal(session_id, user, bot_mode):
    """Create or get existing chat session"""
    from wowdash_app.models import ChatSession
    if not session_id:
        session_id = str(uuid.uuid4())
    try:
        chat_session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            user=user,
            bot_mode=bot_mode,
            defaults={'created_at': now()}
        )
        return chat_session, created
    except Exception as e:
        log_error_to_file(e)

def update_chat_session_title_dal(chat_session, title):
    """Update chat session title"""
    try:
        chat_session.title = title
        chat_session.save()
        return chat_session
    except Exception as e:
        log_error_to_file(e)

def update_chat_session_modified_dal(chat_session):
    """Update chat session modified timestamp"""
    try:
        chat_session.modified_at = now()
        chat_session.save()
        return chat_session
    except Exception as e:
        log_error_to_file(e)

def create_chat_message_dal(session, message, is_bot_response):
    """Create a new chat message"""
    try:
        return ChatMessage.objects.create(
            session=session,
            message=message,
            is_bot_response=is_bot_response,
            timestamp=now()
        )
    except Exception as e:
        log_error_to_file(e)

def get_chat_sessions_by_user_dal(user, bot_mode=None):
    """Get chat sessions for a user"""
    try:
        sessions = ChatSession.objects.filter(user=user)
        if bot_mode:
            sessions = sessions.filter(bot_mode=bot_mode)
        return sessions.values('session_id', 'title', 'modified_at').order_by('-modified_at')
    except Exception as e:
        log_error_to_file(e)

def get_chat_session_by_id_dal(session_id, user):
    """Get specific chat session by ID"""
    try:
        return ChatSession.objects.get(session_id=session_id, user=user)
    except ChatSession.DoesNotExist:
        raise ChatSession.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def get_messages_by_session_dal(chat_session):
    """Get all messages for a chat session"""
    try:
        return ChatMessage.objects.filter(session=chat_session).values(
            'message_id', 'message', 'is_bot_response', 'timestamp', 'feedback_type', 'message_feedback'
        ).order_by('timestamp')
    except Exception as e:
        log_error_to_file(e)

def delete_chat_session_dal(session_id, user):
    """Delete a chat session"""
    try:
        session = ChatSession.objects.get(session_id=session_id, user=user)
        session.delete()
        return True
    except ChatSession.DoesNotExist:
        raise ChatSession.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def update_message_feedback_dal(message_id, feedback_type, message_feedback):
    """Update message feedback"""
    try:
        msg = ChatMessage.objects.get(message_id=message_id)
        msg.feedback_type = feedback_type
        msg.message_feedback = message_feedback
        msg.save()
        return msg
    except ChatMessage.DoesNotExist:
        raise ChatMessage.DoesNotExist
    except Exception as e:
        log_error_to_file(e)

def generate_ai_response_dal(prompt):
    """Generate AI response using Gemini"""
    try:
        response_text = send_message_to_gemini(prompt)
        
        # Ensure response_text is a string
        if not isinstance(response_text, str):
            # Try to extract text if it's a dict/object, fallback to str()
            response_text = getattr(response_text, 'text', None) or getattr(response_text, 'generated_text', None) or str(response_text)
        
        return response_text
    except Exception as e:
        log_error_to_file(e)

def generate_conversation_title_dal(user_input):
    """Generate conversation title"""
    try:
        title_prompt = f"Generate one short title for this message to display as heading: {user_input}"
        return send_message_to_gemini(title_prompt)
    except Exception as e:
        log_error_to_file(e)
