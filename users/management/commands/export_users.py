import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Export User data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'users_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-sensitive',
            action='store_true',
            help='Include sensitive data like passwords',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_sensitive = options['include_sensitive']
        
        # Get all User objects
        users = User.objects.all()
        
        # Serialize to JSON with custom handling for sensitive data
        if include_sensitive:
            data = serialize('json', users)
        else:
            # Create a safe version without passwords and OTP data
            safe_data = []
            for user in users:
                safe_user = {
                    'model': 'auth.user',
                    'pk': user.pk,
                    'fields': {
                        'role': user.role,
                        'phone_number': user.phone_number,
                        'email': user.email,
                        'is_approved': user.is_approved,
                        'is_blocked': user.is_blocked,
                        'is_staff': user.is_staff,
                        'is_active': user.is_active,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                    }
                }
                safe_data.append(safe_user)
            data = json.dumps(safe_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {users.count()} users to {filepath}')
        )