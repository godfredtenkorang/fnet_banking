import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import BankDeposit, Agent
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
            '--skip-missing-agents',
            action='store_true',
            help='Skip deposits with missing agent references',
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
            help='Skip duplicate deposits (by unique combination)',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_missing_agents = options['skip_missing_agents']
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
            missing_agents = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    deposit_data = obj.object
                    
                    # Check if agent exists
                    agent = None
                    if deposit_data.agent_id:
                        try:
                            agent = Agent.objects.get(pk=deposit_data.agent_id)
                        except Agent.DoesNotExist:
                            if skip_missing_agents:
                                missing_agents += 1
                                continue
                            else:
                                raise ValueError(f"Agent with ID {deposit_data.agent_id} does not exist")
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates:
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
                        deposit_data.receipt = self._handle_image_import(deposit_data.receipt, 'branch_receipt_img')
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} bank deposits, '
                    f'skipped {skipped}, '
                    f'missing agents: {missing_agents} from {filepath}'
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