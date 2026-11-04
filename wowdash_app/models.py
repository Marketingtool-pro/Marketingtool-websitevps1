import uuid
from django.contrib.auth.models import User 
from django.db import models
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.urls import reverse

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=[('admin', 'Admin'), ('user', 'User')], default='user')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_active = models.BooleanField(default=True, help_text="Designates whether this user can log in to the website")
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def clean(self):
        # Prevent superusers from deactivating themselves
        if not self.is_active and self.user.is_superuser:
            raise ValidationError("Superusers cannot be deactivated. Please transfer superuser status to another user first.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class UserOTP(models.Model):
    """
    Model to store OTP details for a User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="otp_data")
    reset_otp = models.CharField(max_length=4, null=True, blank=True)
    otp_valid_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OTP Data for {self.user.username}"

    class Meta:
        db_table = 'user_otp'


class ChatSession(models.Model):
    """
    Model to represent a chat session.
    """
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    bot_mode = models.CharField(max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_sessions")
    created_at = models.DateTimeField(default=now)
    modified_at = models.DateTimeField(default=now, editable=True)
    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Session {self.session_id} named {self.title} by {self.user.username} at {self.modified_at}"

    class Meta:
        db_table = 'chat_session'
        ordering = ['-modified_at']


class ChatMessage(models.Model):
    """
    Model to represent individual chat messages within a session.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    feedback_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike'), ('none', 'None')], default='none')
    message_feedback = models.TextField(null=True, blank=True)
    is_bot_response = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"Message in {self.session.session_id} at {self.timestamp}"

    class Meta:
        db_table = 'chat_message'
        ordering = ['timestamp']

class EnvVar(models.Model):
    """
    Represents a single "environment variable" or key/value pair.
    """
    key = models.CharField( max_length=100, unique=True, help_text="The name of the variable")
    value = models.TextField( help_text="The variable's value", null=False, blank=False)
    modified_at = models.DateTimeField( auto_now=True, help_text="Automatically updated when this row changes")

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'env_var'
        ordering = ['key']


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity')
    last_login_time = models.DateTimeField(null=True, blank=True)
    last_logout_time = models.DateTimeField(null=True, blank=True)
    session_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Activity'
    
class ContentSetting(models.Model):
    """
    Model to store content settings for the application.
    """
    key = models.CharField(max_length=100, unique=True, help_text="The name of the setting")
    value = models.TextField(help_text="The setting's value")
    modified_at = models.DateTimeField(auto_now=True, help_text="Automatically updated when this row changes")

    def __str__(self):
        return self.key

    class Meta:
        db_table = 'content_setting'
        ordering = ['key']

class FAQ(models.Model):
    category = models.CharField(max_length=100)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        pass

    def __str__(self):
        return f"{self.category} - {self.question}"

class UserQueries(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        db_table = 'contact_message'
        ordering = ['-created_at']

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='team_photos/')
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.name} - {self.position}"

    def clean(self):
        if self.featured:
            # Count currently featured members excluding self
            featured_count = TeamMember.objects.filter(featured=True).exclude(id=self.id).count()
            if featured_count >= 3:
                raise ValidationError('Maximum of 3 team members can be featured.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='blog/images/')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog-details', kwargs={'slug': self.slug})
    
    def get_tags_as_list(self):
        """
        Convert the tags string to a cleaned list of tags.
        """
        if not self.tags:
            return []
        # Split by comma, strip whitespace, filter out empty strings
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def set_tags_from_list(self, tag_list):
        """
        Set tags from a list of strings.
        """
        cleaned_tags = []
        seen = set()
        for tag in tag_list:
            tag = tag.strip()
            if tag and tag not in seen:  # Remove empty tags and duplicates
                cleaned_tags.append(tag)
                seen.add(tag)
        self.tags = ','.join(cleaned_tags)
    
    def add_tag(self, tag):
        """Add a single tag if it doesn't already exist"""
        if not tag or not tag.strip():
            return
        tag = tag.strip()
        current_tags = self.get_tags_as_list()
        if tag not in current_tags:
            current_tags.append(tag)
            self.tags = ','.join(current_tags)
    
    def has_tag(self, tag):
        """Check if a specific tag exists (case-sensitive)"""
        return tag in self.get_tags_as_list()
    
    @classmethod
    def get_all_unique_tags(cls):
        """Get all unique tags across all blog posts"""
        from django.db.models import F
        return cls.objects.exclude(tags__isnull=True).exclude(tags='').annotate(
            tag=F('tags')  # This will be processed in Python for complex parsing
        ).values_list('tag', flat=True).distinct()
    
    def save(self, *args, **kwargs):
        # Ensure tags are properly formatted before saving
        if self.tags:
            # Normalize tags without changing the visual representation
            tags = [tag.strip() for tag in self.tags.split(',') if tag.strip()]
            self.tags = ','.join(tags)
        super().save(*args, **kwargs)

def validate_feature_types(value):
    """Validate that feature types are valid"""
    valid_types = ['fixed', 'updated', 'improved', 'added']
    if not all(key in valid_types for key in value.keys()):
        raise ValidationError(f'Invalid feature types. Must be one of: {", ".join(valid_types)}')

class ReleaseNote(models.Model):
    FEATURE_TYPES = [
        ('fixed', 'Fixed'),
        ('updated', 'Updated'),
        ('improved', 'Improved'),
        ('added', 'Added'),
    ]

    version = models.CharField(max_length=50, help_text="Version number (e.g., 1.0.0)")
    release_date = models.DateField()
    heading = models.CharField(max_length=200)
    features = models.JSONField(
        help_text="Features organized by type (fixed, updated, improved, added)",
        default=dict,
        validators=[validate_feature_types]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date', '-version']
        verbose_name = "Release Note"
        verbose_name_plural = "Release Notes"

    def __str__(self):
        return f"v{self.version} - {self.heading}"

    def clean(self):
        if self.features:
            invalid_keys = [key for key in self.features.keys() if key not in dict(self.FEATURE_TYPES)]
            if invalid_keys:
                raise ValidationError({
                    'features': f'Invalid feature types: {", ".join(invalid_keys)}. Must be one of: {", ".join(dict(self.FEATURE_TYPES).keys())}'
                })

class UserSession(models.Model):
    """
    Model to track active user sessions across different devices and browsers
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    last_activity = models.DateTimeField(auto_now=True)
    device_info = models.CharField(max_length=255)
    browser_info = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s session on {self.device_info}"

    class Meta:
        db_table = 'user_session'
        ordering = ['-last_activity']

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class GeneratedContent(models.Model):
    CONTENT_TYPES = (('word', 'Word'), ('image', 'Image'))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

# ============================================
# NEW FEATURES - Media, Social, AI, Analytics
# ============================================

class MediaFile(models.Model):
    """Media Library for images, videos, documents"""
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='media_library/%Y/%m/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, default='image')
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    alt_text = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class SocialAccount(models.Model):
    """Connected social media accounts"""
    PLATFORMS = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter/X'),
        ('linkedin', 'LinkedIn'),
        ('tiktok', 'TikTok'),
    ]
    
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    account_name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255, blank=True)
    access_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.account_name} ({self.platform})"


class ScheduledPost(models.Model):
    """Social media post scheduler"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    media = models.ManyToManyField(MediaFile, blank=True)
    platforms = models.ManyToManyField(SocialAccount)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.title} - {self.status}"


class AIBlogDraft(models.Model):
    """AI-generated blog drafts"""
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    topic = models.CharField(max_length=500)
    keywords = models.CharField(max_length=500, blank=True)
    tone = models.CharField(max_length=50, default='professional')
    generated_title = models.CharField(max_length=500, blank=True)
    generated_content = models.TextField(blank=True)
    generated_meta = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    ai_model = models.CharField(max_length=50, default='gemini')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.topic[:50]} - {self.status}"


class WebsiteAnalytics(models.Model):
    """Store daily analytics data"""
    date = models.DateField(unique=True)
    page_views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    bounce_rate = models.FloatField(default=0)
    avg_session_duration = models.PositiveIntegerField(default=0)  # in seconds
    top_pages = models.JSONField(default=dict)
    traffic_sources = models.JSONField(default=dict)
    device_breakdown = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics for {self.date}"


class NewsletterSubscriber(models.Model):
    """Email newsletter subscribers"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    """Email newsletter campaigns"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
    ]
    
    subject = models.CharField(max_length=255)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_time = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_count = models.PositiveIntegerField(default=0)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.subject


class AssistantConversation(models.Model):
    """Personal AI Assistant conversations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class AssistantMessage(models.Model):
    """Messages in AI Assistant conversation"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(AssistantConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."

