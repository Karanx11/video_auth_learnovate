from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Remove duplicate users and clean up database'

    def handle(self, *args, **options):
        # Find and keep only the first user with each email
        seen_emails = {}
        users_to_delete = []
        
        for user in User.objects.all().order_by('id'):
            if user.email in seen_emails:
                users_to_delete.append(user.id)
            else:
                seen_emails[user.email] = user.id
        
        # Delete duplicate users
        if users_to_delete:
            User.objects.filter(id__in=users_to_delete).delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {len(users_to_delete)} duplicate user(s)'))
        else:
            self.stdout.write(self.style.SUCCESS('No duplicates found'))
