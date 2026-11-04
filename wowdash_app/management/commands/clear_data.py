from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import (
    UserProfile, UserActivity, Blog, TeamMember, ReleaseNote,
    UserSession, UserQueries, FAQ, ChatSession, ChatMessage,
    Subscription, GeneratedContent, EnvVar, ContentSetting
)

class Command(BaseCommand):
    help = 'Clears all data except superuser'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to clear data...')
        
        # Store superusers
        superusers = User.objects.filter(is_superuser=True)
        
        # Create profiles for superusers if they don't exist
        for superuser in superusers:
            UserProfile.objects.get_or_create(
                user=superuser,
                defaults={
                    'role': 'admin',
                    'is_active': True
                }
            )
        
        # Store superuser IDs
        superuser_ids = list(superusers.values_list('id', flat=True))
        
        # Clear all data
        GeneratedContent.objects.all().delete()
        Subscription.objects.all().delete()
        ChatMessage.objects.all().delete()
        ChatSession.objects.all().delete()
        UserQueries.objects.all().delete()
        FAQ.objects.all().delete()
        ReleaseNote.objects.all().delete()
        TeamMember.objects.all().delete()
        Blog.objects.all().delete()
        UserSession.objects.all().delete()
        UserActivity.objects.all().delete()
        EnvVar.objects.all().delete()
        ContentSetting.objects.all().delete()
        
        # Delete all user profiles except superusers
        UserProfile.objects.exclude(user_id__in=superuser_ids).delete()
        
        # Delete all users except superusers
        User.objects.exclude(id__in=superuser_ids).delete()
        
        self.stdout.write(self.style.SUCCESS('Successfully cleared data while preserving superusers')) 