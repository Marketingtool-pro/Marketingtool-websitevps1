from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserOTP, ChatMessage, ChatSession, EnvVar, UserProfile, ContentSetting, FAQ, UserQueries, TeamMember, Blog, ReleaseNote, UserSession, Subscription, GeneratedContent
from .models import UserActivity
from django.utils.safestring import mark_safe

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, UserAdmin)
admin.site.register(UserOTP)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('message_id', 'message', 'is_bot_response', 'timestamp', 'feedback_type', 'message_feedback')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'bot_mode', 'created_at', 'modified_at')
    search_fields = ('title', 'user__username')
    list_filter = ('user', 'created_at')
    inlines = [ChatMessageInline]

@admin.register(ContentSetting)
class ContentSettingAdmin(admin.ModelAdmin):
    list_display = ('key',  'modified_at')
    readonly_fields = ('modified_at',)
    search_fields  = ('key',)

@admin.register(EnvVar)
class EnvVarAdmin(admin.ModelAdmin):
    list_display   = ('key', 'modified_at')
    readonly_fields = ('modified_at',)
    search_fields  = ('key',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'department', 'designation', 'is_active', 'profile_picture_link')
    list_filter = ('role', 'is_active')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('profile_picture_link',)
    fields = ('user', 'role', 'is_active', 'department', 'designation', 'profile_picture', 'profile_picture_link')
    
    def profile_picture_link(self, obj):
        try:
            if obj.profile_picture and obj.profile_picture.url:
                return mark_safe(f'<a href="{obj.profile_picture.url}" target="_blank">View Photo</a>')
        except:
            pass
        return "-"
    profile_picture_link.short_description = 'Profile Picture'
    profile_picture_link.allow_tags = True
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.user.is_superuser:
            # Disable the is_active field for superusers
            form.base_fields['is_active'].disabled = True
            form.base_fields['is_active'].help_text = "Superusers cannot be deactivated"
        return form

class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login_time', 'last_logout_time', 'session_duration')
    search_fields = ('user__username',)
    list_filter = ('last_login_time', 'last_logout_time')

admin.site.register(UserActivity, UserActivityAdmin)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'question', 'answer', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(UserQueries)
class UserQueriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'phone', 'message', 'created_at', 'is_read')
    list_filter = ('name', 'is_read')
    search_fields = ('name', 'email')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'featured', 'order', 'photo_link')
    list_editable = ('featured', 'order')
    list_filter = ('featured',)
    search_fields = ('name', 'position')
    ordering = ('order', 'name')
    readonly_fields = ('photo_link',)

    def photo_link(self, obj):
        try:
            if obj.photo and obj.photo.url:
                return mark_safe(f'<a href="{obj.photo.url}" target="_blank">View Photo</a>')
        except:
            pass
        return "-"
    photo_link.short_description = 'Photo'
    photo_link.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['order'].help_text = 'Use this field to control the display order of team members.'
        form.base_fields['featured'].help_text = 'Only 3 team members can be featured. Featured members will be displayed prominently.'
        return form

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'is_published', 'views')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        ('Metadata', {
            'fields': ('author', 'category', 'tags')
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
    )

@admin.register(ReleaseNote)
class ReleaseNoteAdmin(admin.ModelAdmin):
    list_display = ('version', 'release_date', 'heading', 'created_at')
    list_filter = ('release_date',)
    search_fields = ('version', 'heading')
    date_hierarchy = 'release_date'
    ordering = ('-release_date', '-version')

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_info', 'browser_info', 'ip_address', 'last_activity', 'is_active')
    list_filter = ('is_active', 'last_activity', 'browser_info')
    search_fields = ('user__username', 'device_info', 'ip_address')
    readonly_fields = ('session_key', 'user_agent', 'created_at', 'last_activity')
    ordering = ('-last_activity',)
    date_hierarchy = 'last_activity'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'session_key')
        }),
        ('Device Information', {
            'fields': ('device_info', 'browser_info', 'user_agent')
        }),
        ('Session Details', {
            'fields': ('ip_address', 'is_active', 'last_activity', 'created_at')
        }),
    )
    
@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'created_at', 'is_active')
    readonly_fields = ('created_at',)

@admin.register(GeneratedContent)
class GeneratedContentAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username', 'content_type')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Content Details', {
            'fields': ('user', 'content_type', 'content_data')
        }),
    )


# New Feature Models
from .models import MediaFile, SocialAccount, ScheduledPost, AIBlogDraft
from .models import WebsiteAnalytics, NewsletterSubscriber, NewsletterCampaign
from .models import AssistantConversation, AssistantMessage

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'uploaded_by', 'created_at', 'file_size')
    list_filter = ('media_type', 'created_at')
    search_fields = ('title', 'uploaded_by__username')

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('platform', 'account_name', 'account_id', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('account_name', 'account_id')

@admin.register(ScheduledPost)
class ScheduledPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'scheduled_time', 'status', 'published_at', 'created_by')
    list_filter = ('status', 'scheduled_time')
    search_fields = ('title', 'content')

@admin.register(AIBlogDraft)
class AIBlogDraftAdmin(admin.ModelAdmin):
    list_display = ('generated_title', 'topic', 'created_by', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('topic', 'generated_title', 'generated_content')

@admin.register(WebsiteAnalytics)
class WebsiteAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'page_views', 'unique_visitors', 'bounce_rate')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'status', 'created_at', 'sent_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'content')

class AssistantMessageInline(admin.TabularInline):
    model = AssistantMessage
    extra = 0
    readonly_fields = ('role', 'content', 'timestamp')

@admin.register(AssistantConversation)
class AssistantConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at', 'message_count')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'user__username')
    inlines = [AssistantMessageInline]
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

@admin.register(AssistantMessage)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'short_content', 'timestamp')
    list_filter = ('role', 'timestamp')
    search_fields = ('content',)
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'
