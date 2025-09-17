import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Customer
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Customer data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'customers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related User, Agent, Mobilization, and Branch data',
            default=False
        )
        parser.add_argument(
            '--include-images',
            action='store_true',
            help='Include image data (base64 encoded)',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        include_images = options['include_images']
        
        # Get all Customer objects with related data
        customers = Customer.objects.all().select_related('customer', 'agent', 'mobilization', 'branch')
        
        # Serialize to JSON
        if include_related:
            # Include related data
            data = serialize('json', customers, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for customer in customers:
                customer_data = {
                    'model': 'your_app.customer',
                    'pk': customer.pk,
                    'fields': {
                        'customer': customer.customer_id,  # Just the user ID
                        'agent': customer.agent_id if customer.agent else None,
                        'mobilization': customer.mobilization_id if customer.mobilization else None,
                        'branch': customer.branch_id if customer.branch else None,
                        'phone_number': customer.phone_number,
                        'full_name': customer.full_name,
                        'customer_location': customer.customer_location,
                        'digital_address': customer.digital_address,
                        'id_type': customer.id_type,
                        'id_number': customer.id_number,
                        'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                        'customer_picture': self._handle_image(customer.customer_picture, include_images),
                        'customer_image': self._handle_image(customer.customer_image, include_images),
                        'date_created': customer.date_created.isoformat() if customer.date_created else None,
                    }
                }
                custom_data.append(customer_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {customers.count()} customers to {filepath}')
        )
    
    def _handle_image(self, image_field, include_images):
        """Handle image field - either include base64 data or just filename"""
        if not image_field:
            return None
        
        if include_images and image_field:
            # Convert image to base64 for export
            import base64
            try:
                with open(image_field.path, 'rb') as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except (FileNotFoundError, ValueError):
                return None
        else:
            # Just return the filename
            return image_field.name if image_field else None