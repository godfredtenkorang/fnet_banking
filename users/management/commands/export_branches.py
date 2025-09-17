import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Branch
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Branch data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'branches_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

    def handle(self, *args, **options):
        filename = options['filename']
        
        # Get all Branch objects
        branches = Branch.objects.all()
        
        # Serialize to JSON
        data = serialize('json', branches)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {branches.count()} branches to {filepath}')
        )