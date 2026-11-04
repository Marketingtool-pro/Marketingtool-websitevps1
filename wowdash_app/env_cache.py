# env_cache.py
from django.apps import apps

_env_vars: dict[str, str] = {}
_loaded = False

def _load(data: dict[str, str]):
    global _env_vars, _loaded
    _env_vars = data
    _loaded = True
    #print("✅ EnvVars loaded into memory")

def preload_env_vars():
    if not apps.ready:
        #print("⚠️ Apps not ready — skipping preload.")
        return

    try:
        from .models import EnvVar
        rows = EnvVar.objects.all()
        data = {row.key: row.value for row in rows}
        _load(data)
    except Exception as e:
     print("❌ Failed to preload EnvVars:", e)

def get(key: str, default=None):
    return _env_vars.get(key, default)

def all_vars():
    return dict(_env_vars)
