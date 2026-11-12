import os
from django.core import management
from django.core.management.base import BaseCommand, CommandError
from flawedsite.settings import BASE_DIR

class Command(BaseCommand):
    help = "Makes a clean build by reinitiating the database."

    def handle(self, *arg, **options):
        if os.path.exists(str(BASE_DIR) + '/db.sqlite3'):
            management.call_command("migrate", "exam", "zero")
        management.call_command("migrate")
