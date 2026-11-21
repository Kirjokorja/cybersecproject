from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from exam.models import User

class Command(BaseCommand):
    help = "Hashes user passwords in database. " \
    "Ommit users from this process by passing them in arguments. " \
    "Example: hash_password --usernames 'onerva' 'seppo'"

    def add_arguments(self, parser):
        parser.add_argument("--usernames", nargs="*", type=str, help="Users to ommit from hashing.")

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            if user.username not in options["usernames"]:
                user.password = make_password(user.password)
                user.save()
                self.stdout.write(
                self.style.SUCCESS("Hashed password of  '%s'", user.username)
                )
        self.stdout.write(
                self.style.SUCCESS("Finished password hashing.")
            )
