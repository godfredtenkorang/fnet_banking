import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from agent.models import CashAndECashRequest, Agent
from django.db import transaction
import os
from django.conf import settings
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import CashAndECashRequest data from JSON file'

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
            help='Skip requests with missing agent references',
            default=False
        )
        parser.add_argument(
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate requests (by transaction ID or unique combination)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing requests instead of skipping',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_missing_agents = options['skip_missing_agents']
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
                CashAndECashRequest.objects.all().delete()
                self.stdout.write('Cleared existing CashAndECashRequest data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_agents = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    request_data = obj.object
                    
                    # Check if agent exists
                    agent = None
                    if request_data.agent_id:
                        try:
                            agent = Agent.objects.get(pk=request_data.agent_id)
                        except Agent.DoesNotExist:
                            if skip_missing_agents:
                                missing_agents += 1
                                continue
                            else:
                                raise ValueError(f"Agent with ID {request_data.agent_id} does not exist")
                    
                    # Handle amount conversion from string to Decimal
                    if isinstance(request_data.amount, str):
                        try:
                            request_data.amount = Decimal(request_data.amount)
                        except (ValueError, TypeError):
                            request_data.amount = Decimal('0.00')
                    
                    # Handle arrears conversion from string to Decimal
                    if isinstance(request_data.arrears, str):
                        try:
                            request_data.arrears = Decimal(request_data.arrears)
                        except (ValueError, TypeError):
                            request_data.arrears = Decimal('0.00')
                    
                    # Check for duplicates if skip_duplicates is True
                    if skip_duplicates:
                        # Check by transaction_id if available
                        if request_data.transaction_id:
                            existing_request = CashAndECashRequest.objects.filter(
                                transaction_id=request_data.transaction_id
                            ).first()
                            if existing_request:
                                if update_existing:
                                    # Update existing request
                                    existing_request.agent = agent
                                    existing_request.float_type = request_data.float_type
                                    existing_request.bank = request_data.bank
                                    existing_request.network = request_data.network
                                    existing_request.cash = request_data.cash
                                    existing_request.name = request_data.name
                                    existing_request.phone_number = request_data.phone_number
                                    existing_request.amount = request_data.amount
                                    existing_request.arrears = request_data.arrears
                                    existing_request.status = request_data.status
                                    existing_request.save()
                                    updated += 1
                                    continue
                                else:
                                    skipped += 1
                                    continue
                        
                        # Check by unique combination of agent, amount, and created_at
                        existing_request = CashAndECashRequest.objects.filter(
                            agent=agent,
                            amount=request_data.amount,
                            created_at=request_data.created_at
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing request
                                existing_request.float_type = request_data.float_type
                                existing_request.bank = request_data.bank
                                existing_request.transaction_id = request_data.transaction_id
                                existing_request.network = request_data.network
                                existing_request.cash = request_data.cash
                                existing_request.name = request_data.name
                                existing_request.phone_number = request_data.phone_number
                                existing_request.arrears = request_data.arrears
                                existing_request.status = request_data.status
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
                    f'Successfully imported {count} cash/ecash requests, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing agents: {missing_agents} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )