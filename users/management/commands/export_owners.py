import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Owner
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Owner data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'owners_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related User and Branch data',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        
        # Get all Owner objects with related data
        owners = Owner.objects.all().select_related('owner', 'branch')
        
        # Serialize to JSON
        if include_related:
            # Include related User and Branch data
            data = serialize('json', owners, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for owner in owners:
                owner_data = {
                    'model': 'your_app.owner',
                    'pk': owner.pk,
                    'fields': {
                        'owner': owner.owner_id,  # Just the user ID
                        'branch': owner.branch_id if owner.branch else None,  # Just the branch ID
                        'email': owner.email,
                        'full_name': owner.full_name,
                        'phone_number': owner.phone_number,
                        'company_name': owner.company_name,
                        'company_number': owner.company_number,
                        'digital_address': owner.digital_address,
                        'agent_code': owner.agent_code,
                    }
                }
                custom_data.append(owner_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {owners.count()} owners to {filepath}')
        )