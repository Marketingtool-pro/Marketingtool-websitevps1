from django.db import migrations, models

def set_bot_mode_text_generator(apps, schema_editor):
    ChatSession = apps.get_model('wowdash_app', 'ChatSession')
    ChatSession.objects.all().update(bot_mode='text-generator')

class Migration(migrations.Migration):

    dependencies = [
        # Replace with your last migration
        ('wowdash_app', '0025_alter_chatmessage_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatsession',
            name='bot_mode',
            field=models.CharField(max_length=50, null=True),  # Temporarily allow nulls
        ),
        migrations.RunPython(set_bot_mode_text_generator),
        migrations.AlterField(
            model_name='chatsession',
            name='bot_mode',
            field=models.CharField(max_length=50, null=False,),
        ),
    ]