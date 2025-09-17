import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Mobilization
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Mobilization data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'mobilizations_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related User, Owner, and Branch data',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        
        # Get all Mobilization objects with related data
        mobilizations = Mobilization.objects.all().select_related('mobilization', 'owner', 'branch')
        
        # Serialize to JSON
        if include_related:
            # Include related User, Owner, and Branch data
            data = serialize('json', mobilizations, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for mob in mobilizations:
                mob_data = {
                    'model': 'your_app.mobilization',
                    'pk': mob.pk,
                    'fields': {
                        'mobilization': mob.mobilization_id,  # Just the user ID
                        'owner': mob.owner_id if mob.owner else None,  # Just the owner ID
                        'branch': mob.branch_id if mob.branch else None,  # Just the branch ID
                        'email': mob.email,
                        'full_name': mob.full_name,
                        'phone_number': mob.phone_number,
                        'company_name': mob.company_name,
                        'company_number': mob.company_number,
                        'digital_address': mob.digital_address,
                        'mobilization_code': mob.mobilization_code,
                    }
                }
                custom_data.append(mob_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {mobilizations.count()} mobilizations to {filepath}')
        )