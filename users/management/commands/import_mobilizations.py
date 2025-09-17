import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Mobilization, User, Owner, Branch
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Mobilization data from JSON file'

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
            help='Skip duplicate mobilizations (by user)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing mobilizations instead of skipping',
            default=False
        )
        parser.add_argument(
            '--skip-missing-users',
            action='store_true',
            help='Skip mobilizations with missing user references',
            default=False
        )
        parser.add_argument(
            '--skip-missing-owners',
            action='store_true',
            help='Skip mobilizations with missing owner references',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_missing_users = options['skip_missing_users']
        skip_missing_owners = options['skip_missing_owners']
        
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
                Mobilization.objects.all().delete()
                self.stdout.write('Cleared existing Mobilization data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_users = 0
            missing_owners = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    mob_data = obj.object
                    
                    # Check if user exists
                    try:
                        user = User.objects.get(pk=mob_data.mobilization_id)
                    except User.DoesNotExist:
                        if skip_missing_users:
                            missing_users += 1
                            continue
                        else:
                            raise ValueError(f"User with ID {mob_data.mobilization_id} does not exist")
                    
                    # Check if owner exists (if specified)
                    owner = None
                    if mob_data.owner_id:
                        try:
                            owner = Owner.objects.get(pk=mob_data.owner_id)
                        except Owner.DoesNotExist:
                            if skip_missing_owners:
                                missing_owners += 1
                                continue
                            else:
                                raise ValueError(f"Owner with ID {mob_data.owner_id} does not exist")
                    
                    # Check for existing mobilization by user
                    existing_mob = Mobilization.objects.filter(mobilization=user).first()
                    
                    if existing_mob:
                        if skip_duplicates:
                            skipped += 1
                            continue
                        elif update_existing:
                            # Update existing mobilization
                            existing_mob.owner = owner
                            existing_mob.branch = mob_data.branch
                            existing_mob.email = mob_data.email
                            existing_mob.full_name = mob_data.full_name
                            existing_mob.phone_number = mob_data.phone_number
                            existing_mob.company_name = mob_data.company_name
                            existing_mob.company_number = mob_data.company_number
                            existing_mob.digital_address = mob_data.digital_address
                            existing_mob.mobilization_code = mob_data.mobilization_code
                            existing_mob.save()
                            updated += 1
                            continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} mobilizations, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing users: {missing_users}, '
                    f'missing owners: {missing_owners} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )