import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from models import Agent
from django.utils import timezone
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Export Agent data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--filename',
            type=str,
            help='Output filename (optional)',
            default=f'agents_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        parser.add_argument(
            '--include-related',
            action='store_true',
            help='Include related User, Owner, and Branch data',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        include_related = options['include_related']
        
        # Get all Agent objects with related data
        agents = Agent.objects.all().select_related('agent', 'owner', 'branch')
        
        # Serialize to JSON
        if include_related:
            # Include related User, Owner, and Branch data
            data = serialize('json', agents, use_natural_foreign_keys=True)
        else:
            # Create custom serialization without full related objects
            custom_data = []
            for agent in agents:
                agent_data = {
                    'model': 'your_app.agent',
                    'pk': agent.pk,
                    'fields': {
                        'agent': agent.agent_id,  # Just the user ID
                        'owner': agent.owner_id,  # Just the owner ID
                        'branch': agent.branch_id if agent.branch else None,  # Just the branch ID
                        'email': agent.email,
                        'full_name': agent.full_name,
                        'phone_number': agent.phone_number,
                        'company_name': agent.company_name,
                        'company_number': agent.company_number,
                        'digital_address': agent.digital_address,
                        'agent_code': agent.agent_code,
                    }
                }
                custom_data.append(agent_data)
            data = json.dumps(custom_data)
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Write to file
        filepath = os.path.join(backup_dir, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {agents.count()} agents to {filepath}')
        )