import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from django.contrib.auth import get_user_model
from django.db import transaction
import os
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Import User data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Input filename (required)',
            required=True
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing data before import',
            default=False
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate phone numbers',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        
        filepath = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        if not os.path.exists(filepath):
            self.stdout.write(
                self.style.ERROR(f'File not found: {filepath}')
            )
            return
        
        try:
            with open(filepath, 'r') as f:
                data = f.read()
            
            # Clear existing data if requested
            if clear_existing:
                User.objects.all().delete()
                self.stdout.write('Cleared existing User data')
            
            # Deserialize and save objects
            count = 0
            skipped = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    user_data = obj.object
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates and User.objects.filter(phone_number=user_data.phone_number).exists():
                        skipped += 1
                        continue
                    
                    # Handle password properly for new users
                    if not user_data.password.startswith(('pbkdf2_', 'bcrypt$', 'argon2$')):
                        # If password is not properly hashed, set a default password
                        user_data.set_password('default_password')
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {count} users, skipped {skipped} duplicates from {filepath}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )