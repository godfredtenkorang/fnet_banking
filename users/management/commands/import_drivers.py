import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Driver, User
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Driver data from JSON file'

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
            help='Skip duplicate drivers (by user)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing drivers instead of skipping',
            default=False
        )
        parser.add_argument(
            '--skip-missing-users',
            action='store_true',
            help='Skip drivers with missing user references',
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
                Driver.objects.all().delete()
                self.stdout.write('Cleared existing Driver data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_users = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    driver_data = obj.object
                    
                    # Check if user exists
                    try:
                        user = User.objects.get(pk=driver_data.driver_id)
                    except User.DoesNotExist:
                        if skip_missing_users:
                            missing_users += 1
                            continue
                        else:
                            raise ValueError(f"User with ID {driver_data.driver_id} does not exist")
                    
                    # Check for existing driver by user
                    existing_driver = Driver.objects.filter(driver=user).first()
                    
                    if existing_driver:
                        if skip_duplicates:
                            skipped += 1
                            continue
                        elif update_existing:
                            # Update existing driver
                            existing_driver.email = driver_data.email
                            existing_driver.full_name = driver_data.full_name
                            existing_driver.phone_number = driver_data.phone_number
                            existing_driver.company_name = driver_data.company_name
                            existing_driver.company_number = driver_data.company_number
                            existing_driver.digital_address = driver_data.digital_address
                            existing_driver.driver_code = driver_data.driver_code
                            existing_driver.save()
                            updated += 1
                            continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} drivers, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing users: {missing_users} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )