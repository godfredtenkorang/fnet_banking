import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from agent.models import PaymentRequest
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export PaymentRequest data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'payment_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
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
        
        # Get all PaymentRequest objects with related data
        payment_requests = PaymentRequest.objects.all().select_related('agent')
        
        # Serialize to JSON
        if include_related:
            # Include related data
            data = serialize('json', payment_requests, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for payment_request in payment_requests:
                payment_request_data = {
                    'model': 'your_app.paymentrequest',
                    'pk': payment_request.pk,
                    'fields': {
                        'agent': payment_request.agent_id if payment_request.agent else None,
                        'mode_of_payment': payment_request.mode_of_payment,
                        'bank': payment_request.bank,
                        'network': payment_request.network,
                        'branch': payment_request.branch,
                        'name': payment_request.name,
                        'branch_transaction_id': payment_request.branch_transaction_id,
                        'amount': str(payment_request.amount),  # Convert Decimal to string
                        'status': payment_request.status,
                        'created_at': payment_request.created_at.isoformat() if payment_request.created_at else None,
                        'time_created': payment_request.time_created.isoformat() if payment_request.time_created else None,
                        'updated_at': payment_request.updated_at.isoformat() if payment_request.updated_at else None,
                    }
                }
                custom_data.append(payment_request_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {payment_requests.count()} payment requests to {filepath}')
        )