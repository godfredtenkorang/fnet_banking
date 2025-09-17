import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from mobilization.models import PaymentRequest, Mobilization
from django.db import transaction
import os
from django.conf import settings
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import PaymentRequest data from JSON file'

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
            help='Skip payment requests with missing mobilization references',
            default=False
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate payment requests (by transaction ID)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing payment requests instead of skipping',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_missing_mobilizations = options['skip_missing_mobilizations']
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
                PaymentRequest.objects.all().delete()
                self.stdout.write('Cleared existing PaymentRequest data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_mobilizations = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    payment_request_data = obj.object
                    
                    # Check if mobilization exists
                    mobilization = None
                    if payment_request_data.mobilization_id:
                        try:
                            mobilization = Mobilization.objects.get(pk=payment_request_data.mobilization_id)
                        except Mobilization.DoesNotExist:
                            if skip_missing_mobilizations:
                                missing_mobilizations += 1
                                continue
                            else:
                                raise ValueError(f"Mobilization with ID {payment_request_data.mobilization_id} does not exist")
                    
                    # Handle amount conversion from string to Decimal
                    if isinstance(payment_request_data.amount, str):
                        try:
                            payment_request_data.amount = Decimal(payment_request_data.amount)
                        except (ValueError, TypeError):
                            payment_request_data.amount = Decimal('0.00')
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates:
                        # Check by mobilization_transaction_id if available
                        if payment_request_data.mobilization_transaction_id:
                            existing_request = PaymentRequest.objects.filter(
                                mobilization_transaction_id=payment_request_data.mobilization_transaction_id
                            ).first()
                            if existing_request:
                                if update_existing:
                                    # Update existing payment request
                                    existing_request.mobilization = mobilization
                                    existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                    existing_request.bank = payment_request_data.bank
                                    existing_request.network = payment_request_data.network
                                    existing_request.branch = payment_request_data.branch
                                    existing_request.name = payment_request_data.name
                                    existing_request.amount = payment_request_data.amount
                                    existing_request.owner_transaction_id = payment_request_data.owner_transaction_id
                                    existing_request.status = payment_request_data.status
                                    existing_request.save()
                                    updated += 1
                                    continue
                                else:
                                    skipped += 1
                                    continue
                        
                        # Check by owner_transaction_id if available
                        if payment_request_data.owner_transaction_id:
                            existing_request = PaymentRequest.objects.filter(
                                owner_transaction_id=payment_request_data.owner_transaction_id
                            ).first()
                            if existing_request:
                                if update_existing:
                                    # Update existing payment request
                                    existing_request.mobilization = mobilization
                                    existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                    existing_request.bank = payment_request_data.bank
                                    existing_request.network = payment_request_data.network
                                    existing_request.branch = payment_request_data.branch
                                    existing_request.name = payment_request_data.name
                                    existing_request.amount = payment_request_data.amount
                                    existing_request.mobilization_transaction_id = payment_request_data.mobilization_transaction_id
                                    existing_request.status = payment_request_data.status
                                    existing_request.save()
                                    updated += 1
                                    continue
                                else:
                                    skipped += 1
                                    continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} payment requests, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing mobilizations: {missing_mobilizations} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )