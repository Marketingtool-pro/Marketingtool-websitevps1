import re

from wowdash_app.utils import log_error_to_file
from Dal.aiwave.tools import (
    create_or_get_chat_session_dal,
    update_chat_session_title_dal,
    update_chat_session_modified_dal,
    create_chat_message_dal,
    get_chat_sessions_by_user_dal,
    get_chat_session_by_id_dal,
    get_messages_by_session_dal,
    delete_chat_session_dal,
    update_message_feedback_dal,
    generate_ai_response_dal,
    generate_conversation_title_dal
)

def strip_markdown(text):
    # Remove bold, italics, inline code, and links
    text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)  # bold
    text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)      # italics
    text = re.sub(r'`([^`]*)`', r'\1', text)            # inline code
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)  # links
    return text.strip()

def process_text_generation_bal(user_input, session_id, user, bot_mode):
    """Process text generation request"""
    try:
        # Create or get chat session
        chat_session, created = create_or_get_chat_session_dal(session_id, user, bot_mode)
        
        # Generate title for new sessions
        if created:
            conversation_title = generate_conversation_title_dal(user_input)
            update_chat_session_title_dal(chat_session, conversation_title)
        else:
            conversation_title = chat_session.title
        
        # Generate system prompt based on bot mode
        system_prompt = generate_system_prompt_bal(user_input, bot_mode)
        
        # Generate AI response
        response_text = generate_ai_response_dal(system_prompt)
        
        # Save messages
        create_chat_message_dal(chat_session, user_input, False)
        bot_message = create_chat_message_dal(chat_session, response_text, True)
        
        # Update session modified timestamp
        update_chat_session_modified_dal(chat_session)
        
        return {
            'generated_text': response_text,
            'message_id': bot_message.message_id,
            'session_id': chat_session.session_id,
            'chat_history': {
                'title': conversation_title
            }
        }
    except Exception as e:
        log_error_to_file(e)

def generate_system_prompt_bal(user_input, bot_mode):
    """Generate system prompt based on bot mode"""
    prompts = {
        'email-generator': f"Write an email: {user_input}",
        'summary-generator': f"Summarize this: {user_input}",
        'code-generator': f"Generate code for: {user_input}",
        'description-generator': f"Generate a description for: {user_input}",
        'blog-generator': f"Write a blog post about: {user_input}",
        'text-generator': f"Generate a response for: {user_input}"
    }
    return prompts.get(bot_mode, f"Generate a response for: {user_input}")

def get_user_sessions_bal(user, bot_mode=None):
    """Get user's chat sessions"""
    try:
        sessions = get_chat_sessions_by_user_dal(user, bot_mode)
        return list(sessions)
    except Exception as e:
        log_error_to_file(e)

def get_session_messages_bal(session_id, user):
    """Get messages for a specific session"""
    try:
        chat_session = get_chat_session_by_id_dal(session_id, user)
        messages = get_messages_by_session_dal(chat_session)
        
        return {
            'messages': list(messages),
            'session_title': chat_session.title
        }
    except Exception as e:
        log_error_to_file(e)

def delete_user_session_bal(session_id, user):
    """Delete a user's chat session"""
    try:
        return delete_chat_session_dal(session_id, user)
    except Exception as e:
        log_error_to_file(e)

def update_message_feedback_bal(message_id, feedback_type, message_feedback):
    """Update message feedback"""
    try:
        if feedback_type not in ['like', 'dislike', 'none']:
            raise ValueError("Invalid feedback type")
        
        return update_message_feedback_dal(message_id, feedback_type, message_feedback)
    except Exception as e:
        log_error_to_file(e)
