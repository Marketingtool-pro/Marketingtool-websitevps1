from Dal.wowdash_app.wowdash import (
    get_user_query_by_id, delete_user_query, delete_all_read_inquiries, get_all_user_queries,
    get_blogs_filtered, get_blog_categories,
    get_active_faq_categories, get_active_faqs,
    get_all_release_notes, get_release_note_by_pk, delete_release_note,
    create_faq, get_faq_by_id, update_faq, delete_faq, toggle_faq_visibility,
    get_content_setting, set_content_setting,
    get_all_team_members, create_team_member, get_team_member_by_id, update_team_member, delete_team_member
)
from collections import defaultdict
from django.core.paginator import Paginator

# User Inquiries BAL

def mark_query_as_read(query_id):
    query = get_user_query_by_id(query_id)
    query.is_read = True
    query.save()
    return query

def delete_query_by_id(query_id):
    query = get_user_query_by_id(query_id)
    delete_user_query(query)
    return True

def delete_all_read_queries():
    return delete_all_read_inquiries()

def get_user_inquiries(show_unread=False, query_id=None):
    queries = get_all_user_queries()
    if show_unread:
        queries = queries.filter(is_read=False)
    queries = queries.order_by('is_read', '-created_at')
    if query_id:
        try:
            query = queries.get(id=query_id)
            queries = [query]
        except Exception:
            queries = []
    return queries

# FAQ BAL

def get_faqs_grouped_by_category():
    faqs = get_active_faqs()
    faqs_by_category = defaultdict(list)
    for faq in faqs:
        faqs_by_category[faq.category].append(faq)
    return dict(faqs_by_category)

def get_faq_categories():
    return get_active_faq_categories()

def create_faq_bal(category, question, answer, is_active=True):
    return create_faq(category, question, answer, is_active)

def edit_faq_bal(faq_id, category, question, answer, is_active):
    faq = get_faq_by_id(faq_id)
    return update_faq(faq, category, question, answer, is_active)

def delete_faq_bal(faq_id):
    faq = get_faq_by_id(faq_id)
    delete_faq(faq)
    return True

def toggle_faq_visibility_bal(faq_id, is_active):
    faq = get_faq_by_id(faq_id)
    return toggle_faq_visibility(faq, is_active)

# ContentSetting BAL
def get_terms_content():
    return get_content_setting('terms_conditions')

def set_terms_content(value):
    return set_content_setting('terms_conditions', value)

def get_privacy_content():
    return get_content_setting('privacy_conditions')

def set_privacy_content(value):
    return set_content_setting('privacy_conditions', value)

# TeamMember BAL
def get_team_members():
    return get_all_team_members()

def add_team_member_bal(name, position, photo, order, featured):
    return create_team_member(name, position, photo, order, featured)

def edit_team_member_bal(member_id, name, position, order, featured, photo=None):
    member = get_team_member_by_id(member_id)
    return update_team_member(member, name, position, order, featured, photo)

def delete_team_member_bal(member_id):
    member = get_team_member_by_id(member_id)
    delete_team_member(member)
    return True

# Blog BAL

def get_blogs_with_filters(search_query, status, selected_category, page_number, per_page=10):
    posts = get_blogs_filtered(search_query, status, selected_category)
    paginator = Paginator(posts, per_page)
    return paginator.get_page(page_number)

def get_blog_categories_with_counts():
    return get_blog_categories()

# Release Note BAL

def get_release_notes():
    return get_all_release_notes()

def delete_release_note_by_pk(pk):
    note = get_release_note_by_pk(pk)
    delete_release_note(note)
    return True
