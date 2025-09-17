import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from mobilization.models import BankDeposit, Mobilization
from django.db import transaction
import os
from django.conf import settings
import base64
from django.core.files.base import ContentFile
from decimal import Decimal
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import BankDeposit data from JSON file'

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
            '--skip-missing-mobilizations',
            action='store_true',
            help='Skip deposits with missing mobilization references',
            default=False
        )
        parser.add_argument(
            '--handle-images',
            action='store_true',
            help='Handle image data during import',
            default=False
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate deposits (by transaction ID or unique combination)',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_missing_mobilizations = options['skip_missing_mobilizations']
        handle_images = options['handle_images']
        skip_duplicates = options['skip_duplicates']
        
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
                BankDeposit.objects.all().delete()
                self.stdout.write('Cleared existing BankDeposit data')
            
            # Deserialize and save objects
            count = 0
            skipped = 0
            missing_mobilizations = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    deposit_data = obj.object
                    
                    # Check if mobilization exists (if specified)
                    mobilization = None
                    if deposit_data.mobilization_id:
                        try:
                            mobilization = Mobilization.objects.get(pk=deposit_data.mobilization_id)
                        except Mobilization.DoesNotExist:
                            if skip_missing_mobilizations:
                                missing_mobilizations += 1
                                continue
                            else:
                                raise ValueError(f"Mobilization with ID {deposit_data.mobilization_id} does not exist")
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates:
                        # Check by owner_transaction_id if available
                        if deposit_data.owner_transaction_id:
                            existing_deposit = BankDeposit.objects.filter(
                                owner_transaction_id=deposit_data.owner_transaction_id
                            ).first()
                            if existing_deposit:
                                skipped += 1
                                continue
                        
                        # Check by unique combination of bank, account_number, amount, and date
                        existing_deposit = BankDeposit.objects.filter(
                            bank=deposit_data.bank,
                            account_number=deposit_data.account_number,
                            amount=deposit_data.amount,
                            date_deposited=deposit_data.date_deposited
                        ).first()
                        if existing_deposit:
                            skipped += 1
                            continue
                    
                    # Handle amount conversion from string to Decimal
                    if isinstance(deposit_data.amount, str):
                        try:
                            deposit_data.amount = Decimal(deposit_data.amount)
                        except (ValueError, TypeError):
                            deposit_data.amount = Decimal('0.00')
                    
                    # Handle images if specified
                    if handle_images:
                        deposit_data.receipt = self._handle_image_import(deposit_data.receipt, 'receipt_img')
                        deposit_data.screenshot = self._handle_image_import(deposit_data.screenshot, 'screenshot_img')
                        deposit_data.screenshot2 = self._handle_image_import(deposit_data.screenshot2, 'screenshot_img2')
                        deposit_data.screenshot3 = self._handle_image_import(deposit_data.screenshot3, 'screenshot_img3')
                        deposit_data.screenshot4 = self._handle_image_import(deposit_data.screenshot4, 'screenshot_img4')
                        deposit_data.screenshot5 = self._handle_image_import(deposit_data.screenshot5, 'screenshot_img5')
                        deposit_data.screenshot6 = self._handle_image_import(deposit_data.screenshot6, 'screenshot_img6')
                        deposit_data.screenshot7 = self._handle_image_import(deposit_data.screenshot7, 'screenshot_img7')
                        deposit_data.screenshot8 = self._handle_image_import(deposit_data.screenshot8, 'screenshot_img8')
                        deposit_data.screenshot9 = self._handle_image_import(deposit_data.screenshot9, 'screenshot_img9')
                        deposit_data.screenshot10 = self._handle_image_import(deposit_data.screenshot10, 'screenshot_img10')
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} bank deposits, '
                    f'skipped {skipped}, '
                    f'missing mobilizations: {missing_mobilizations} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )
    
    def _handle_image_import(self, image_data, upload_to):
        """Handle image import - decode base64 or return None"""
        if not image_data:
            return None
        
        # Check if it's base64 encoded
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            try:
                # Extract base64 data from data URL
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
                return data
            except (ValueError, TypeError):
                return None
        elif isinstance(image_data, str) and len(image_data) > 100:  # Likely base64 without data URL
            try:
                data = ContentFile(base64.b64decode(image_data), name=f'{upload_to}_{timezone.now().timestamp()}.png')
                return data
            except (ValueError, TypeError):
                return None
        return image_data