from django.db import migrations
from django.contrib.auth.models import User

def add_users(apps, schema_editor):
    User.objects.create_superuser(username="admin", email="admin@admin.example", password="thesuperboss")
    User.objects.create_user(username="seppo", password="smithingismylife")
    User.objects.create_user(username="onerva", password="letsplayhayday")

def remove_users(apps, schema_editor):
    User.objects.all().delete()

def forward(apps, schema_editor):
    add_users(apps, schema_editor)

def reverse(apps, schema_editor):
    remove_users(apps, schema_editor)

class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
