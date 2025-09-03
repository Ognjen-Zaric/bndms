from django.core.management.base import BaseCommand
from api.models import Account

class Command(BaseCommand):
    help = 'Update user authority levels'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to update')
        parser.add_argument('authority_level', type=str, choices=['N', 'L', 'E', 'O', 'A'], 
                          help='Authority level: N=None, L=Logged In, E=Emergency Worker, O=Organizer, A=Admin')

    def handle(self, *args, **options):
        username = options['username']
        authority_level = options['authority_level']
        
        try:
            user = Account.objects.get(username=username)
            old_level = user.get_authority_level_display()
            user.authority_level = authority_level
            user.save()
            new_level = user.get_authority_level_display()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {username} from "{old_level}" to "{new_level}"'
                )
            )
        except Account.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            )
