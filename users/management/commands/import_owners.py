import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Owner, User
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Owner data from JSON file'

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
            help='Skip duplicate owners (by user)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing owners instead of skipping',
            default=False
        )
        parser.add_argument(
            '--skip-missing-users',
            action='store_true',
            help='Skip owners with missing user references',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_missing_users = options['skip_missing_users']
        
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
                Owner.objects.all().delete()
                self.stdout.write('Cleared existing Owner data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_users = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    owner_data = obj.object
                    
                    # Check if user exists
                    try:
                        user = User.objects.get(pk=owner_data.owner_id)
                    except User.DoesNotExist:
                        if skip_missing_users:
                            missing_users += 1
                            continue
                        else:
                            raise ValueError(f"User with ID {owner_data.owner_id} does not exist")
                    
                    # Check for existing owner by user
                    existing_owner = Owner.objects.filter(owner=user).first()
                    
                    if existing_owner:
                        if skip_duplicates:
                            skipped += 1
                            continue
                        elif update_existing:
                            # Update existing owner
                            existing_owner.branch = owner_data.branch
                            existing_owner.email = owner_data.email
                            existing_owner.full_name = owner_data.full_name
                            existing_owner.phone_number = owner_data.phone_number
                            existing_owner.company_name = owner_data.company_name
                            existing_owner.company_number = owner_data.company_number
                            existing_owner.digital_address = owner_data.digital_address
                            existing_owner.agent_code = owner_data.agent_code
                            existing_owner.save()
                            updated += 1
                            continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} owners, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing users: {missing_users} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )