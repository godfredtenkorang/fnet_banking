import json
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from models import Agent, User, Owner, Branch
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Import Agent data from JSON file'

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
            '--skip-duplicates',
            action='store_true',
            help='Skip duplicate agents (by user)',
            default=False
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing agents instead of skipping',
            default=False
        )
        parser.add_argument(
            '--skip-missing-users',
            action='store_true',
            help='Skip agents with missing user references',
            default=False
        )
        parser.add_argument(
            '--skip-missing-owners',
            action='store_true',
            help='Skip agents with missing owner references',
            default=False
        )

    def handle(self, *args, **options):
        filename = options['filename']
        clear_existing = options['clear_existing']
        skip_duplicates = options['skip_duplicates']
        update_existing = options['update_existing']
        skip_missing_users = options['skip_missing_users']
        skip_missing_owners = options['skip_missing_owners']
        
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
                Agent.objects.all().delete()
                self.stdout.write('Cleared existing Agent data')
            
            # Deserialize and save objects
            count = 0
            updated = 0
            skipped = 0
            missing_users = 0
            missing_owners = 0
            with transaction.atomic():
                for obj in deserialize('json', data):
                    agent_data = obj.object
                    
                    # Check if user exists
                    try:
                        user = User.objects.get(pk=agent_data.agent_id)
                    except User.DoesNotExist:
                        if skip_missing_users:
                            missing_users += 1
                            continue
                        else:
                            raise ValueError(f"User with ID {agent_data.agent_id} does not exist")
                    
                    # Check if owner exists
                    try:
                        owner = Owner.objects.get(pk=agent_data.owner_id)
                    except Owner.DoesNotExist:
                        if skip_missing_owners:
                            missing_owners += 1
                            continue
                        else:
                            raise ValueError(f"Owner with ID {agent_data.owner_id} does not exist")
                    
                    # Check for existing agent by user
                    existing_agent = Agent.objects.filter(agent=user).first()
                    
                    if existing_agent:
                        if skip_duplicates:
                            skipped += 1
                            continue
                        elif update_existing:
                            # Update existing agent
                            existing_agent.owner = owner
                            existing_agent.branch = agent_data.branch
                            existing_agent.email = agent_data.email
                            existing_agent.full_name = agent_data.full_name
                            existing_agent.phone_number = agent_data.phone_number
                            existing_agent.company_name = agent_data.company_name
                            existing_agent.company_number = agent_data.company_number
                            existing_agent.digital_address = agent_data.digital_address
                            existing_agent.agent_code = agent_data.agent_code
                            existing_agent.save()
                            updated += 1
                            continue
                    
                    obj.save()
                    count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully imported {count} agents, '
                    f'updated {updated}, skipped {skipped}, '
                    f'missing users: {missing_users}, '
                    f'missing owners: {missing_owners} from {filepath}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing data: {str(e)}')
            )