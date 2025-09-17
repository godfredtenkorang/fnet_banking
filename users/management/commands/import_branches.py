import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Branch
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Branch data from JSON file'

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
            help='Skip duplicate branch names',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing branches instead of skipping',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        
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
                Branch.objects.all().delete()
                self.stdout.write('Cleared existing Branch data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    branch_data = obj.object
                    
                    # Check for existing branch by name
                    existing_branch = None
                    if branch_data.name:
                        existing_branch = Branch.objects.filter(name=branch_data.name).first()
                    
                    if existing_branch:
                        if skip_duplicates:
                            skipped += 1
                            continue
                        elif update_existing:
                            # Update existing branch
                            existing_branch.location = branch_data.location
                            existing_branch.save()
                            updated += 1
                            continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} branches, '
                    f'updated {updated}, skipped {skipped} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )