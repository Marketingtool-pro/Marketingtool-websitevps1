from wowdash_app.models import UserQueries, Blog, FAQ, ReleaseNote, ContentSetting, TeamMember
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

# UserQueries DAL

def get_user_query_by_id(query_id):
    return UserQueries.objects.get(id=query_id)

def delete_user_query(query):
    query.delete()

def delete_all_read_inquiries():
    return UserQueries.objects.filter(is_read=True).delete()

def get_all_user_queries():
    return UserQueries.objects.all()

def get_blogs_filtered(search_query=None, status=None, selected_category=None):
    posts = Blog.objects.all().order_by('-created_at')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    if status:
        posts = posts.filter(is_published=(status == 'published'))
    if selected_category:
        posts = posts.filter(category=selected_category)
    return posts

def get_blog_categories():
    return Blog.objects.values('category').annotate(count=Count('id')).order_by('category')

# FAQ DAL

def get_active_faq_categories():
    return FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct()

def get_active_faqs():
    return FAQ.objects.filter(is_active=True)

def create_faq(category, question, answer, is_active=True):
    return FAQ.objects.create(
        category=category,
        question=question,
        answer=answer,
        is_active=is_active
    )

def get_faq_by_id(faq_id):
    return FAQ.objects.get(id=faq_id)

def update_faq(faq, category, question, answer, is_active):
    faq.category = category
    faq.question = question
    faq.answer = answer
    faq.is_active = is_active
    faq.save()
    return faq

def delete_faq(faq):
    faq.delete()

def toggle_faq_visibility(faq, is_active):
    faq.is_active = is_active
    faq.save()
    return faq

# ReleaseNote DAL

def get_all_release_notes():
    return ReleaseNote.objects.all().order_by('-release_date')

def get_release_note_by_pk(pk):
    return get_object_or_404(ReleaseNote, pk=pk)

def delete_release_note(note):
    note.delete()

# ContentSetting DAL (for terms and privacy)
def get_content_setting(key):
    return ContentSetting.objects.filter(key=key).first()

def set_content_setting(key, value):
    obj = ContentSetting.objects.filter(key=key).first()
    if obj:
        obj.value = value
        obj.save()
    else:
        obj = ContentSetting.objects.create(key=key, value=value)
    return obj

# TeamMember DAL
def get_all_team_members():
    return TeamMember.objects.all().order_by('-featured', 'order', 'name')

def create_team_member(name, position, photo, order, featured):
    return TeamMember.objects.create(
        name=name,
        position=position,
        photo=photo,
        order=order,
        featured=featured
    )

def get_team_member_by_id(member_id):
    return TeamMember.objects.get(id=member_id)

def update_team_member(member, name, position, order, featured, photo=None):
    member.name = name
    member.position = position
    member.order = order
    member.featured = featured
    if photo:
        member.photo = photo
    member.save()
    return member

def delete_team_member(member):
    member.delete()
