import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from agent.models import PaymentRequest, Agent
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
            '--skip-missing-agents',
            action='store_true',
            help='Skip payment requests with missing agent references',
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
        parser.add_argument(
            '--skip-duplicate-transaction-id',
            action='store_true',
            help='Skip payment requests with duplicate branch_transaction_id',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_missing_agents = options['skip_missing_agents']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_duplicate_transaction_id = options['skip_duplicate_transaction_id']
        
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
            missing_agents = 0
            duplicate_transaction_ids = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    payment_request_data = obj.object
                    
                    # Check if agent exists
                    agent = None
                    if payment_request_data.agent_id:
                        try:
                            agent = Agent.objects.get(pk=payment_request_data.agent_id)
                        except Agent.DoesNotExist:
                            if skip_missing_agents:
                                missing_agents += 1
                                continue
                            else:
                                raise ValueError(f"Agent with ID {payment_request_data.agent_id} does not exist")
                    
                    # Handle amount conversion from string to Decimal
                    if isinstance(payment_request_data.amount, str):
                        try:
                            payment_request_data.amount = Decimal(payment_request_data.amount)
                        except (ValueError, TypeError):
                            payment_request_data.amount = Decimal('0.00')
                    
                    # Check for duplicate branch_transaction_id if specified
                    if skip_duplicate_transaction_id and payment_request_data.branch_transaction_id:
                        existing_with_same_id = PaymentRequest.objects.filter(
                            branch_transaction_id=payment_request_data.branch_transaction_id
                        ).exists()
                        if existing_with_same_id:
                            duplicate_transaction_ids += 1
                            continue
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates:
                        # Check by unique combination of agent, amount, and created_at
                        existing_request = PaymentRequest.objects.filter(
                            agent=agent,
                            amount=payment_request_data.amount,
                            created_at=payment_request_data.created_at
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing payment request
                                existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                existing_request.bank = payment_request_data.bank
                                existing_request.network = payment_request_data.network
                                existing_request.branch = payment_request_data.branch
                                existing_request.name = payment_request_data.name
                                existing_request.branch_transaction_id = payment_request_data.branch_transaction_id
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
                    f'missing agents: {missing_agents}, '
                    f'duplicate transaction IDs: {duplicate_transaction_ids} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )