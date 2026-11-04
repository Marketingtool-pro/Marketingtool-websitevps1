# apps.py
from django.apps import AppConfig

class WowdashAppConfig(AppConfig):
    name = "wowdash_app"

    def ready(self):
        import wowdash_app.signals  # Connect post_save/delete signals

        # Delay DB cache preload using threading
        from threading import Timer
        from .env_cache import preload_env_vars

        Timer(1.0, preload_env_vars).start()  # Wait 1 sec, then load cache
