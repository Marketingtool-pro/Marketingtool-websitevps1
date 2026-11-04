import json
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from wowdash_app.utils import log_error_to_file
from Bal.aiwave.tools import (
    process_text_generation_bal,
    get_user_sessions_bal,
    get_session_messages_bal,
    delete_user_session_bal,
    update_message_feedback_bal,
    strip_markdown
)

def handle_generator_request(request, bot_mode, template_name, page_title):
    """
    Reusable function to handle generator requests (both POST and GET)
    
    Args:
        request: Django request object
        bot_mode: The bot mode (e.g., 'text-generator', 'blog-generator', 'code-generator')
        template_name: The template to render
        page_title: The title for the page
    
    Returns:
        JsonResponse for POST requests, render for GET requests
    """
    if request.method == 'POST':
        user_input = request.POST.get('chatMessage', '').strip()
        session_id = request.POST.get('sessionId')
        request_bot_mode = request.POST.get('botMode')

        if not user_input:
            return JsonResponse({'error': 'Input text is required.'}, status=400)

        if not session_id:
            return JsonResponse({'error': 'Session ID is required.'}, status=400)

        try:
            result = process_text_generation_bal(user_input, session_id, request.user, request_bot_mode)
            return JsonResponse(result)
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'error': 'An error occurred.'}, status=500)
    
    # Handle GET with prompt from homepage
    prompt = request.GET.get('prompt', '').strip()
    initial_chat = None
    if prompt:
        # Generate a new session id (could be uuid or similar, here just use None to let DAL create it)
        session_id = None
        try:
            result = process_text_generation_bal(prompt, session_id, request.user if request.user.is_authenticated else None, bot_mode)
            # Strip markdown from the generated title ONLY for this flow
            if result and 'chat_history' in result and 'title' in result['chat_history']:
                result['chat_history']['title'] = strip_markdown(result['chat_history']['title'])
            initial_chat = {
                'user_input': prompt,
                'bot_response': result.get('generated_text'),
                'session_id': result.get('session_id'),
                'chat_history': result.get('chat_history', {})
            }
        except Exception as e:
            log_error_to_file(e)
            initial_chat = {'error': 'An error occurred while generating the response.'}
    
    return render(request, template_name, {
        'title': page_title,
        'subtitle': page_title,
        'initial_chat': initial_chat,
        'bot_mode': bot_mode,
    })


def textGenerator(request):
    return handle_generator_request(request, 'text-generator', 'tools/textGenerator.html', 'Text Generator')


@login_required
def getSessions(request):
    try:
        bot_mode = request.GET.get('botMode')
        sessions = get_user_sessions_bal(request.user, bot_mode)
        return JsonResponse({'sessions': sessions})
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'error': 'Failed to fetch sessions.'}, status=500)
    

@login_required
def getMessages(request):
    if request.method == 'GET':
        session_id = request.GET.get('sessionId')

        if not session_id:
            return JsonResponse({'error': 'Session ID is required.'}, status=400)

        try:
            result = get_session_messages_bal(session_id, request.user)
            return JsonResponse(result)

        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'error': 'Failed to fetch messages.'}, status=500)


def summaryGenerator(request):
    return handle_generator_request(request, 'summary-generator', 'tools/summaryGenerator.html', 'Summary Generator')


def descriptionGenerator(request):
    return handle_generator_request(request, 'description-generator', 'tools/descriptionGenerator.html', 'Description Generator')


def blogGenerator(request):
    return handle_generator_request(request, 'blog-generator', 'tools/blogGenerator.html', 'Blog Generator')  


def emailGenerator(request):
    return handle_generator_request(request, 'email-generator', 'tools/emailGenerator.html', 'Email Generator')


def codeGenerator(request):
    return handle_generator_request(request, 'code-generator', 'tools/codeGenerator.html', 'Code Generator')


@login_required
@require_http_methods(["DELETE"])
def deleteSession(request, session_id):
    try:
        delete_user_session_bal(session_id, request.user)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'status': 'error', 'message': 'An error occurred.'}, status=500)
    


def setFeedback(request):
    data = json.loads(request.body)
    message_id = data.get('message_id')
    feedback_type = data.get('feedback_type')
    message_feedback = data.get('message_feedback', '')

    if message_id and feedback_type in ['like', 'dislike', 'none']:
        try:
            update_message_feedback_bal(message_id, feedback_type, message_feedback)
            return JsonResponse({'success': True})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'error': 'An error occurred.'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)