import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Driver
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Driver data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'drivers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related User data',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        
        # Get all Driver objects with related data
        drivers = Driver.objects.all().select_related('driver')
        
        # Serialize to JSON
        if include_related:
            # Include related User data
            data = serialize('json', drivers, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for driver in drivers:
                driver_data = {
                    'model': 'your_app.driver',
                    'pk': driver.pk,
                    'fields': {
                        'driver': driver.driver_id,  # Just the user ID
                        'email': driver.email,
                        'full_name': driver.full_name,
                        'phone_number': driver.phone_number,
                        'company_name': driver.company_name,
                        'company_number': driver.company_number,
                        'digital_address': driver.digital_address,
                        'driver_code': driver.driver_code,
                    }
                }
                custom_data.append(driver_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {drivers.count()} drivers to {filepath}')
        )