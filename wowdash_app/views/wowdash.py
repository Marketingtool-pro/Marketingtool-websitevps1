from django.contrib import messages
from django.shortcuts import  render, redirect, get_object_or_404
from ..utils import log_error_to_file, log_and_redirect_to_error_page
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from ..models import Blog, ReleaseNote
from django import forms
from Bal.wowdash_app.wowdash import (
    delete_query_by_id, delete_all_read_queries, get_user_inquiries,
    get_faqs_grouped_by_category, get_faq_categories,
    get_blogs_with_filters, get_blog_categories_with_counts,
    get_release_notes, delete_release_note_by_pk,
    create_faq_bal, edit_faq_bal, delete_faq_bal, toggle_faq_visibility_bal,
    get_terms_content, set_terms_content, get_privacy_content, set_privacy_content,
    get_team_members, add_team_member_bal, edit_team_member_bal, delete_team_member_bal,
    get_user_query_by_id
)


def userInquiries(request):
    try:
        show_unread = request.GET.get('unread', 'false') == 'true'
        query_id = request.GET.get('query_id')
        queries = get_user_inquiries(show_unread, query_id)
    
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'userInquiries.html', {
            'title': 'User Inquiries',
            'subtitle': 'Inquiries',
            'custom_css': 'assets/css/custom/wowdash_app/customUserInquiries.css',
            'script': 'assets/js/custom/wowdash_app/customUserInquiries.js',
            'queries': queries,
            'show_unread': show_unread
        })
    


def toggleQueryRead(request, query_id):
    if request.method == 'POST':
        try:
            inquiry = get_user_query_by_id(query_id)
            inquiry.is_read = not inquiry.is_read
            inquiry.save()
            return JsonResponse({'success': True, 'is_read': inquiry.is_read, 'alert': {'type': 'success', 'message': 'Query status updated.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def deleteQuery(request, query_id):
    if request.method == 'POST':
        try:
            delete_query_by_id(query_id)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'Query deleted successfully.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)

def deleteAllReadInquiries(request):
    if request.method == 'POST':
        try:
            deleted_count, _ = delete_all_read_queries()
            messages.success(request, f"Deleted {deleted_count} read inquiries.", extra_tags="secondary")
        except Exception as e:
            log_error_to_file(e)
            messages.error(request, "An error occurred. Please try again.", extra_tags="warning")
    return redirect('userInquiries')



def faq(request):
    try:
        faq_categories = get_faq_categories()
        faqs_by_category = get_faqs_grouped_by_category()
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    
    return render(request, 'faq.html', {
            'title': 'FAQ',
            'subtitle': 'FAQ',
            'custom_css': 'assets/css/custom/wowdash_app/customFaq.css',
            'script': 'assets/js/custom/wowdash_app/customFaq.js',
            'faq_categories': faq_categories,
            'faqs_by_category': faqs_by_category,
        })



def faqCreate(request):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            question = request.POST.get('question')
            answer = request.POST.get('answer')
            is_active = request.POST.get('is_active', 'true') == 'true'
            if not (category and question and answer):
                return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'All fields are required.'}}, status=400)
            faq = create_faq_bal(category, question, answer, is_active)
            return JsonResponse({
                'success': True,
                'faq': {
                    'category_name': faq.category,
                    'question': faq.question,
                    'answer': faq.answer,
                    'is_active': faq.is_active,
                },
                'alert': {'type': 'success', 'message': 'FAQ created successfully.'}
            })
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def faqEdit(request, faq_id):
    if request.method == 'POST':
        try:
            category = request.POST.get('category')
            question = request.POST.get('question')
            answer = request.POST.get('answer')
            is_active = request.POST.get('is_active', 'true') == 'true'
            edit_faq_bal(faq_id, category, question, answer, is_active)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'FAQ updated successfully.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def faqDelete(request, faq_id):
    if request.method == 'POST':
        try:
            delete_faq_bal(faq_id)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'FAQ deleted successfully.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def faqToggleVisibility(request, faq_id):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            is_active = data.get('is_active', False)
            toggle_faq_visibility_bal(faq_id, is_active)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'FAQ visibility updated.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def team(request):
    team_members = get_team_members()
    context = {
        'title': 'Our Team',
        'subtitle': 'Meet Our Team',
        'script': 'assets/js/custom/wowdash_app/customTeam.js',
        'all_members': team_members
    }
    return render(request, 'team.html', context)


def add_team_member(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            position = request.POST.get('position')
            photo = request.FILES.get('photo')
            order = request.POST.get('order', 0)
            featured = request.POST.get('featured', 'false') == 'true'
            if not all([name, position, photo]):
                return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Name, position, and photo are required.'}}, status=400)
            member = add_team_member_bal(name, position, photo, order, featured)
            return JsonResponse({
                'success': True,
                'member': {
                    'id': member.id,
                    'name': member.name,
                    'position': member.position,
                    'photo_url': member.photo.url,
                    'featured': member.featured
                },
                'alert': {'type': 'success', 'message': 'Team member added successfully.'}
            })
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def delete_team_member(request, member_id):
    if request.method == 'POST':
        try:
            delete_team_member_bal(member_id)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'Team member deleted successfully.'}})
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)


def edit_team_member(request, member_id):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            position = request.POST.get('position')
            order = request.POST.get('order', 0)
            featured = request.POST.get('featured', 'false') == 'true'
            photo = request.FILES.get('photo') if 'photo' in request.FILES else None
            edit_team_member_bal(member_id, name, position, order, featured, photo)
            return JsonResponse({'success': True, 'alert': {'type': 'success', 'message': 'Team member updated successfully.'}})
        except ValidationError as e:
            log_error_to_file(e)
            error_message = "Maximum of 3 team members can be featured." if "featured" in str(e) else str(e)
            return JsonResponse({'success': False, 'alert': {'type': 'warning', 'message': error_message}}, status=400)
        except Exception as e:
            log_error_to_file(e)
            return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'An error occurred.'}}, status=500)
    return JsonResponse({'success': False, 'alert': {'type': 'danger', 'message': 'Invalid request method.'}}, status=405)

def pricing(request):
    return render(request, 'pricing.html', {
        'title': 'Pricing',
        'subtitle': 'Pricing'
    })

def termsCondition(request):
    try:
        terms_content = get_terms_content()
        if request.method == 'POST':
            content = request.POST.get('terms-editor-content')
            if content:
                if not terms_content or terms_content.value != content:
                    set_terms_content(content)
                    messages.success(request, "Terms & Conditions updated successfully!")
            return redirect('termsCondition')
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    return render(request, 'termsCondition.html', {
        'title': 'Terms & Conditions',
        'subtitle': 'Terms & Conditions',
        'custom_css': 'assets/css/custom/wowdash_app/customTermsCondition.css',
        'terms_content': terms_content.value if terms_content else '',
        'multi_script': ['assets/js/editor.highlighted.min.js', 
                        'assets/js/editor.quill.js', 
                        'assets/js/editor.katex.min.js',
                        'assets/js/custom/wowdash_app/customTermsCondition.js']
    })

def privacyPolicy(request):
    try:
        privacy_content = get_privacy_content()
        if request.method == 'POST':
            content = request.POST.get('privacy-editor-content')
            if content:
                if not privacy_content or privacy_content.value != content:
                    set_privacy_content(content)
                    messages.success(request, "Privacy Policy updated successfully!")
            return redirect('privacyPolicy')
    except Exception as e:
        return log_and_redirect_to_error_page(e)
    return render(request, 'privacyPolicy.html', {
        'title': 'Privacy Policy',
        'subtitle': 'Privacy Policy',
        'privacy_content': privacy_content.value if privacy_content else '',
        'custom_css': 'assets/css/custom/wowdash_app/customPrivacyPolicy.css',
        'multi_script': ['assets/js/editor.highlighted.min.js', 
                        'assets/js/editor.quill.js', 
                        'assets/js/editor.katex.min.js',
                        'assets/js/custom/wowdash_app/customPrivacyPolicy.js']
    })

def blogManagement(request):
    try:
        search_query = request.GET.get('search', '')
        status = request.GET.get('status', '')
        selected_category = request.GET.get('category', '')
        page_number = request.GET.get('page')
        posts = get_blogs_with_filters(search_query, status, selected_category, page_number)
        categories = get_blog_categories_with_counts()
        context = {
            'title': 'Blog Management',
            'subtitle': 'Blog Management',
            'posts': posts,
            'categories': categories,
            'search_query': search_query,
            'status': status,
            'selected_category': selected_category,
        }
    except Exception as e:
        log_error_to_file(e)
    return render(request, 'blog.html', context)

def editBlog(request, post_id):
    try:
        post = get_object_or_404(Blog, id=post_id)

        if request.method == 'POST':
            # Handle blog update
            post.title = request.POST.get('title')
            post.content = request.POST.get('content')
            post.excerpt = request.POST.get('excerpt')
            post.category = request.POST.get('category')
            
            # Process tags - split by comma, clean, and remove duplicates
            tags_input = request.POST.get('tags', '')
            tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            
            # Use the model's set_tags_from_list method to handle tag processing
            post.set_tags_from_list(tags)
            
            post.is_published = request.POST.get('is_published') == 'on'

            if 'featured_image' in request.FILES:
                post.featured_image = request.FILES['featured_image']

            post.save()
            messages.success(request, 'Blog post updated successfully.')
            return redirect('blogManagement')

        # For GET requests, pass the post with existing tags
        context = {
            'post': post,
            'is_edit': True
        }
        
    except Exception as e:
        log_error_to_file(e)
        
        # In case of error, make sure we still have a valid context
        if 'context' not in locals():
            context = {'post': post, 'is_edit': True}

    return render(request, 'blog.html', context)

def blogDelete(request, post_id):
    try:
        if request.method == 'POST':
            post = get_object_or_404(Blog, id=post_id)
            post.delete()
            messages.success(request, 'Blog post deleted successfully.', extra_tags="secondary")
            return redirect('blogManagement')
    except Exception as e:
        log_error_to_file(e)

    return redirect('blogManagement')

def blogPreview(request, post_id):
    post = get_object_or_404(Blog, id=post_id)
    return render(request, 'blog.html', {'post': post, 'is_preview': True}) 

class ReleaseNoteForm(forms.ModelForm):
    class Meta:
        model = ReleaseNote
        fields = ['version', 'release_date', 'heading', 'features']

def releaseNotes(request):
    try:
        release_notes = get_release_notes()
        form = ReleaseNoteForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                messages.success(request, "Release note added successfully!", extra_tags="secondary")
                return redirect('releaseNotes')
            else:
                messages.error(request, "Please try again", extra_tags="warning")
        context = {
            'release_notes': release_notes,
            'form': form,
            'title': 'Release Note',
            'subtitle': 'Release Note',
        }
        return render(request, 'releaseNote.html', {
            'script': 'assets/js/custom/wowdash_app/customReleaseNote.js',
            'custom_css': 'assets/css/custom/wowdash_app/customReleaseNote.css',
             **context
            })
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def releaseNoteDelete(request, pk):
    try:
        if request.method == "POST":
            try:
                delete_release_note_by_pk(pk)
            except Exception:
                messages.error(request, "Release note not found.", extra_tags="warning")
                return redirect('releaseNotes')
        return redirect('releaseNotes')
    except Exception as e:
        log_error_to_file(e)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

