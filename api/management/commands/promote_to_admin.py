from django.core.management.base import BaseCommand
from api.models import Account

class Command(BaseCommand):
    help = 'Promote a user to admin status'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to promote to admin')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = Account.objects.get(username=username)
            old_level = user.get_authority_level_display()
            user.authority_level = 'A'
            user.is_staff = True  # Allow Django admin access
            user.is_superuser = True  # Full admin privileges
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully promoted {username} from "{old_level}" to "Admin" with full Django admin access'
                )
            )
        except Account.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
