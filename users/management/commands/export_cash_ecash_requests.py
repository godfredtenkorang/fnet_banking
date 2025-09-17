import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from agent.models import CashAndECashRequest
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export CashAndECashRequest data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'cash_ecash_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related Agent data',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        
        # Get all CashAndECashRequest objects with related data
        requests = CashAndECashRequest.objects.all().select_related('agent')
        
        # Serialize to JSON
        if include_related:
            # Include related data
            data = serialize('json', requests, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for request in requests:
                request_data = {
                    'model': 'your_app.cashandecashrequest',
                    'pk': request.pk,
                    'fields': {
                        'agent': request.agent_id if request.agent else None,
                        'float_type': request.float_type,
                        'bank': request.bank,
                        'transaction_id': request.transaction_id,
                        'network': request.network,
                        'cash': request.cash,
                        'name': request.name,
                        'phone_number': request.phone_number,
                        'amount': str(request.amount),  # Convert Decimal to string
                        'arrears': str(request.arrears),  # Convert Decimal to string
                        'status': request.status,
                        'created_at': request.created_at.isoformat() if request.created_at else None,
                        'time_created': request.time_created.isoformat() if request.time_created else None,
                        'updated_at': request.updated_at.isoformat() if request.updated_at else None,
                    }
                }
                custom_data.append(request_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {requests.count()} cash/ecash requests to {filepath}')
        )