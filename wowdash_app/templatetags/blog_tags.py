from django import template
from wowdash_app.models import Blog

register = template.Library()

@register.filter(name='blog_count')
def blog_count(category):
    """
    Returns the count of published blog posts in a given category
    """
    return Blog.objects.filter(category=category, is_published=True).count() 