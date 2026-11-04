from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import EnvVar
from .env_cache import _load
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .models import UserActivity

# Social login signal (django-allauth)
from allauth.account.signals import user_logged_in as social_user_logged_in

def handle_login(sender, request, user, **kwargs):
    # Always create a new activity record on login
    UserActivity.objects.create(
        user=user,
        last_login_time=timezone.now()
    )

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    handle_login(sender, request, user, **kwargs)

@receiver(social_user_logged_in)
def on_social_user_logged_in(sender, request, user, **kwargs):
    handle_login(sender, request, user, **kwargs)

@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    
    # Check if user is still saved in database before filtering related objects
    if user.pk is None:
        return  # User has been deleted, skip processing
    
    # Update the latest activity record for this user
    activity = UserActivity.objects.filter(user=user, last_logout_time__isnull=True).order_by('-last_login_time').first()
    if activity and activity.last_login_time:
        logout_time = timezone.now()
        activity.last_logout_time = logout_time
        activity.session_duration = logout_time - activity.last_login_time
        activity.save()


# Signal to refresh the environment variable cache when EnvVar instances are saved or deleted.
@receiver([post_save, post_delete], sender=EnvVar)
def refresh_env_cache(sender, **kwargs):
    rows = EnvVar.objects.all()
    data = {r.key: r.value for r in rows}
    _load(data)
