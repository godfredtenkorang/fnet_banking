import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import CustomerAccount
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import CustomerAccount data from JSON file'

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

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        
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
                CustomerAccount.objects.all().delete()
                self.stdout.write('Cleared existing CustomerAccount data')
            
            # Deserialize and save objects
            count = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {count} accounts from {filepath}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )