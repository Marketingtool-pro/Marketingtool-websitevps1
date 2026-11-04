from django.db import migrations
import uuid

def generate_unique_message_ids(apps, schema_editor):
    ChatMessage = apps.get_model('wowdash_app', 'ChatMessage')
    for msg in ChatMessage.objects.filter(message_id__isnull=True):
        msg.message_id = f"msg-{uuid.uuid4().hex[:12]}"
        msg.save(update_fields=['message_id'])

class Migration(migrations.Migration):

    dependencies = [
        ('wowdash_app', '0018_chatmessage_feedback_type_chatmessage_message_id'),
    ]

    operations = [
        migrations.RunPython(generate_unique_message_ids),
    ]
