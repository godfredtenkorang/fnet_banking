import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from mobilization.models import BankDeposit
from django.utils import timezone
import os
from django.conf import settings
import base64

class Command(BaseCommand):
    help = 'Export BankDeposit data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'bank_deposits_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related Mobilization data',
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
        
        # Get all BankDeposit objects with related data
        deposits = BankDeposit.objects.all().select_related('mobilization')
        
        # Serialize to JSON
        if include_related:
            # Include related data
            data = serialize('json', deposits, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for deposit in deposits:
                deposit_data = {
                    'model': 'your_app.bankdeposit',
                    'pk': deposit.pk,
                    'fields': {
                        'mobilization': deposit.mobilization_id if deposit.mobilization else None,
                        'phone_number': deposit.phone_number,
                        'bank': deposit.bank,
                        'account_number': deposit.account_number,
                        'account_name': deposit.account_name,
                        'amount': str(deposit.amount),  # Convert Decimal to string
                        'receipt': self._handle_image(deposit.receipt, include_images),
                        'owner_transaction_id': deposit.owner_transaction_id,
                        'screenshot': self._handle_image(deposit.screenshot, include_images),
                        'screenshot2': self._handle_image(deposit.screenshot2, include_images),
                        'screenshot3': self._handle_image(deposit.screenshot3, include_images),
                        'screenshot4': self._handle_image(deposit.screenshot4, include_images),
                        'screenshot5': self._handle_image(deposit.screenshot5, include_images),
                        'screenshot6': self._handle_image(deposit.screenshot6, include_images),
                        'screenshot7': self._handle_image(deposit.screenshot7, include_images),
                        'screenshot8': self._handle_image(deposit.screenshot8, include_images),
                        'screenshot9': self._handle_image(deposit.screenshot9, include_images),
                        'screenshot10': self._handle_image(deposit.screenshot10, include_images),
                        'status': deposit.status,
                        'date_deposited': deposit.date_deposited.isoformat() if deposit.date_deposited else None,
                        'time_deposited': deposit.time_deposited.isoformat() if deposit.time_deposited else None,
                    }
                }
                custom_data.append(deposit_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {deposits.count()} bank deposits to {filepath}')
        )
    
    def _handle_image(self, image_field, include_images):
        """Handle image field - either include base64 data or just filename"""
        if not image_field:
            return None
        
        if include_images and image_field:
            # Convert image to base64 for export
            try:
                with open(image_field.path, 'rb') as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            except (FileNotFoundError, ValueError):
                return None
        else:
            # Just return the filename
            return image_field.name if image_field else None